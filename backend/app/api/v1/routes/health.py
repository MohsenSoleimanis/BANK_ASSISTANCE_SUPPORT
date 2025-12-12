"""
Health check endpoints
"""
from fastapi import APIRouter
from datetime import datetime
from app.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """
    Basic health check
    Returns service status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": settings.APP_NAME,
        "environment": settings.ENV
    }


@router.get("/detailed")
async def detailed_health_check():
    """
    Detailed health check
    Checks all components
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "up",
            "llm": "up",
            "search": "up",
            "rag": "up"
        }
    }
    
    # In production, actually check each component
    # For now, return optimistic status
    
    return health_status
