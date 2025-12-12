"""
Chat service - passes conversation history to LLM naturally
"""
from typing import Dict, Optional
from uuid import uuid4
from app.core.orchestrator.agent import banking_agent
from app.core.session.manager import session_manager
from app.models.chat import ChatResponse, Source
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatService:
    """Business logic for chat operations"""
    
    def __init__(self):
        self.agent = banking_agent
        self.session_manager = session_manager
    
    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> ChatResponse:
        """Process user message with conversation history"""
        try:
            if not session_id:
                session_id = str(uuid4())
                logger.info(f"New session: {session_id}")
            
            # Get conversation history
            history = self.session_manager.get_history(session_id, last_n=6)
            
            # Pass history to agent (it will format for LLM)
            result = await self.agent.process_query(
                query=message,
                conversation_history=history
            )
            
            # Store this exchange
            self.session_manager.add_message(session_id, "user", message)
            self.session_manager.add_message(session_id, "assistant", result.get("answer", ""))
            
            # Format response
            sources = [Source(**src) for src in result.get("sources", [])]
            
            response = ChatResponse(
                answer=result.get("answer", "I couldn't process that."),
                sources=sources,
                method=result.get("method", "unknown"),
                session_id=session_id,
                escalate=result.get("escalate", False)
            )
            
            logger.info(f"Session {session_id}, method: {response.method}")
            return response
            
        except Exception as e:
            logger.error(f"Error: {e}")
            raise
    
    def get_session_history(self, session_id: str):
        return self.session_manager.get_history(session_id, last_n=50)
    
    def clear_session(self, session_id: str):
        self.session_manager.clear_session(session_id)


chat_service = ChatService()