"""
Chat API endpoints
"""
from fastapi import APIRouter, HTTPException, status
from app.models.chat import ChatRequest, ChatResponse, ErrorResponse
from app.services.chat_service import chat_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest):
    """
    Send a message and get AI response
    
    - **message**: User message (required)
    - **session_id**: Optional session ID for conversation continuity
    - **context**: Optional additional context
    
    Returns AI-generated response with sources and citations
    """
    try:
        logger.info(f"Received chat request: '{request.message[:50]}...'")
        
        response = await chat_service.process_message(
            message=request.message,
            session_id=request.session_id,
            context=request.context
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Get conversation history for a session
    
    - **session_id**: Session identifier
    
    Returns conversation history
    """
    try:
        history = chat_service.get_session_history(session_id)
        
        if not history:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        return {"session_id": session_id, "history": history}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving history"
        )


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a conversation session
    
    - **session_id**: Session to clear
    
    Returns confirmation
    """
    try:
        chat_service.clear_session(session_id)
        return {"message": f"Session {session_id} cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error clearing session"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "chat",
        "version": "1.0.0"
    }
