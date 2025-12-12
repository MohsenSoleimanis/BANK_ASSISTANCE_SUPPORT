"""
Session manager using Redis for conversation history
"""
import json
import redis
from typing import List, Dict, Optional
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Manages conversation sessions with Redis"""
    
    def __init__(self):
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            self.redis_client.ping()
            logger.info("Connected to Redis for session management")
        except Exception as e:
            logger.warning(f"Redis not available: {e}. Using in-memory storage.")
            self.redis_client = None
            self.memory_storage = {}
    
    def add_message(self, session_id: str, role: str, content: str):
       """Add a message to conversation history"""
       try:
           print(f"[DEBUG] Storing message - Session: {session_id}, Role: {role}")
        
           if self.redis_client:
               key = f"session:{session_id}"
               message = {"role": role, "content": content}
               self.redis_client.rpush(key, json.dumps(message))
               self.redis_client.expire(key, 3600)
               print(f"[DEBUG] Stored in Redis - Key: {key}")
           else:
               print(f"[DEBUG] Redis not available, using memory")
               if session_id not in self.memory_storage:
                   self.memory_storage[session_id] = []
               self.memory_storage[session_id].append({"role": role, "content": content})
               print(f"[DEBUG] Memory storage now has: {len(self.memory_storage[session_id])} messages")
       except Exception as e:
           logger.error(f"Error adding message: {e}")
           print(f"[DEBUG ERROR] {e}")
    
    def get_history(self, session_id: str, last_n: int = 6) -> List[Dict]:
        """Get conversation history"""
        try:
            print(f"[DEBUG] Getting history - Session: {session_id}, Last N: {last_n}")
            
            if self.redis_client:
                key = f"session:{session_id}"
                messages = self.redis_client.lrange(key, -last_n, -1)
                result = [json.loads(msg) for msg in messages]
                print(f"[DEBUG] Retrieved from Redis: {len(result)} messages")
                return result
            else:
                history = self.memory_storage.get(session_id, [])
                result = history[-last_n:] if history else []
                print(f"[DEBUG] Retrieved from memory: {len(result)} messages")
                return result
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            print(f"[DEBUG ERROR] {e}")
            return []
    
    def clear_session(self, session_id: str):
        """Clear a session"""
        try:
            if self.redis_client:
                self.redis_client.delete(f"session:{session_id}")
            else:
                if session_id in self.memory_storage:
                    del self.memory_storage[session_id]
        except Exception as e:
            logger.error(f"Error clearing session: {e}")


# Global session manager
session_manager = SessionManager()
