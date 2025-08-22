import os
import json
import uuid
import sqlite3
from monoai.models import Model
import datetime
from pymongo import MongoClient

class BaseHistory:

    def __init__(self, 
                 path: str, 
                 last_n: int=None): 
        self._history_path = path
        self._last_n = last_n
        
    def generate_chat_id(self):
        return str(uuid.uuid4())

    def load(self):
        pass

    def store(self, chat_id: str, messages: list):
        # Aggiungi un timestamp ISO 8601 a ciascun messaggio
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        for msg in messages:
            if 'timestamp' not in msg:
                msg['timestamp'] = now
        return messages

    def clear(self):
        pass


class JSONHistory(BaseHistory):
    
    def __init__(self, 
                 path, 
                 last_n: int=None): 
        self._history_path = path
        self._last_n = last_n
        if not os.path.exists(self._history_path):
            os.makedirs(self._history_path)

    def load(self, chat_id: str):
        # Ensure proper path construction with os.path.join
        file_path = os.path.join(self._history_path, chat_id + ".json")
        with open(file_path, "r") as f:
            self.messages = json.load(f)
        if self._last_n is not None and len(self.messages) > (self._last_n+1)*2:
            self.messages = [self.messages[0]]+self.messages[-self._last_n*2:]
        return self.messages
    
    def new(self, system_prompt: str):
        chat_id = self.generate_chat_id()
        # Ensure directory exists before storing
        if not os.path.exists(self._history_path):
            os.makedirs(self._history_path, exist_ok=True)
        self.store(chat_id, [{"role": "system", "content": system_prompt}])
        return chat_id

    def store(self, chat_id: str, messages: list):
        messages = super().store(chat_id, messages)
        # Load existing messages
        file_path = os.path.join(self._history_path, chat_id + ".json")
        try:
            with open(file_path, "r") as f:
                existing_messages = json.load(f)
        except FileNotFoundError:
            existing_messages = []
        
        # Add the new messages (già con timestamp)
        new_messages = existing_messages + messages
        
        with open(file_path, "w") as f:
            json.dump(new_messages, f, indent=4)

class SQLiteHistory(BaseHistory):
    
    def __init__(self, path: str="histories/chat.db", last_n: int=None):
        self._db_path = path
        self._last_n = last_n
        self._init_db()
    
    def _init_db(self):
        os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    chat_id TEXT,
                    order_index INTEGER,
                    role TEXT,
                    content TEXT,
                    PRIMARY KEY (chat_id, order_index)
                )
            """)
    
    def load(self, chat_id: str):
        with sqlite3.connect(self._db_path) as conn:
            if self._last_n is not None:
                # Get system message
                cursor = conn.execute(
                    "SELECT role, content FROM messages WHERE chat_id = ? AND order_index = 0",
                    (chat_id,)
                )
                system_message = cursor.fetchone()
                
                # Get last N messages
                cursor = conn.execute(
                    """
                    SELECT role, content 
                    FROM messages 
                    WHERE chat_id = ? 
                    ORDER BY order_index DESC 
                    LIMIT ?
                    """,
                    (chat_id, self._last_n * 2)
                )
                last_messages = [{"role": role, "content": content} for role, content in cursor]
                last_messages.reverse()  # Reverse to get correct order
                
                # Combine system message with last N messages
                self.messages = [{"role": system_message[0], "content": system_message[1]}] + last_messages
            else:
                cursor = conn.execute(
                    "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY order_index",
                    (chat_id,)
                )
                self.messages = [{"role": role, "content": content} for role, content in cursor]
        return self.messages
    
    def new(self, system_prompt: str):
        chat_id = self.generate_chat_id()
        self.store(chat_id, [{"role": "system", "content": system_prompt, "order_index": 0}])
        return chat_id

    def store(self, chat_id: str, messages: list):
        messages = super().store(chat_id, messages)
        with sqlite3.connect(self._db_path) as conn:
            # Get the last order_index
            cursor = conn.execute(
                "SELECT MAX(order_index) FROM messages WHERE chat_id = ?",
                (chat_id,)
            )
            last_index = cursor.fetchone()[0]
            
            # If no messages exist yet, start from -1
            if last_index is None:
                last_index = -1
            
            # Insert the new messages con timestamp
            for i, message in enumerate(messages, start=last_index + 1):
                conn.execute(
                    "INSERT INTO messages (chat_id, order_index, role, content) VALUES (?, ?, ?, ?)",
                    (chat_id, i, message["role"], message["content"])
                )
                conn.commit()
        

class DictHistory(BaseHistory):
    """
    In-memory history storage using Python dictionaries.
    Useful for testing and temporary conversations.
    """
    
    def __init__(self, last_n: int = None):
        self._last_n = last_n
        self._histories = {}  # Dictionary to store chat histories
    
    def load(self, chat_id: str):
        if chat_id not in self._histories:
            self.messages = []
            return self.messages
        
        messages = self._histories[chat_id]
        if self._last_n is not None and len(messages) > (self._last_n + 1) * 2:
            messages = [messages[0]] + messages[-self._last_n * 2:]
        
        self.messages = messages
        return self.messages
    
    def new(self, system_prompt: str):
        chat_id = self.generate_chat_id()
        messages = [{"role": "system", "content": system_prompt}]
        self.store(chat_id, messages)
        return chat_id
    
    def store(self, chat_id: str, messages: list):
        messages = super().store(chat_id, messages)
        
        if chat_id not in self._histories:
            self._histories[chat_id] = []
        
        # Add the new messages (già con timestamp)
        self._histories[chat_id].extend(messages)
    
    def clear(self, chat_id: str):
        """Clear history for a specific chat."""
        if chat_id in self._histories:
            del self._histories[chat_id]
    
    def clear_all(self):
        """Clear all chat histories."""
        self._histories.clear()
    
    def get_all_chat_ids(self):
        """Get all chat IDs currently stored."""
        return list(self._histories.keys())
    
    def get_chat_count(self):
        """Get the total number of chats stored."""
        return len(self._histories)


class MongoDBHistory(BaseHistory):
    def __init__(self, db_path, db_name: str = "chat", collection_name: str = "histories", last_n: int = None):
        self._uri = db_path
        self._db_name = db_name
        self._collection_name = collection_name
        self._last_n = last_n
        self._client = MongoClient(self._uri)
        self._db = self._client[self._db_name]
        self._collection = self._db[self._collection_name]

    def load(self, chat_id: str):
        doc = self._collection.find_one({"chat_id": chat_id})
        if not doc:
            self.messages = []
            return self.messages
        messages = doc.get("messages", [])
        if self._last_n is not None and len(messages) > (self._last_n + 1) * 2:
            messages = [messages[0]] + messages[-self._last_n * 2:]
        self.messages = messages
        return self.messages

    def new(self, system_prompt: str):
        chat_id = self.generate_chat_id()
        messages = [{"role": "system", "content": system_prompt}]
        self.store(chat_id, messages)
        return chat_id

    def store(self, chat_id: str, messages: list):
        messages = super().store(chat_id, messages)
        # Get existing messages
        doc = self._collection.find_one({"chat_id": chat_id})
        existing_messages = doc.get("messages", []) if doc else []
        
        # Add the new messages (già con timestamp)
        new_messages = existing_messages + messages
        
        self._collection.update_one(
            {"chat_id": chat_id},
            {"$set": {"messages": new_messages}},
            upsert=True
        )


class HistorySummarizer():

    def __init__(self, model: Model, max_tokens: int=None):
        self._model = model
        self._max_tokens = max_tokens

    def summarize(self, messages: list):
        response = self._model.ask("Summarize the following conversation: "+json.dumps(messages))
        response = response["response"]
        return response

