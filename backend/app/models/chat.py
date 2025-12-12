"""
Pydantic models for chat API
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., description="Message role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Request to chat endpoint"""
    message: str = Field(..., description="User message", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "What are your current savings account interest rates?",
                "session_id": "abc-123",
                "context": {}
            }
        }


class Source(BaseModel):
    """Source information for citations"""
    source: Optional[str] = None
    url: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    score: Optional[float] = None


class ChatResponse(BaseModel):
    """Response from chat endpoint"""
    answer: str = Field(..., description="Generated answer")
    sources: List[Source] = Field(default_factory=list, description="Source citations")
    method: str = Field(..., description="Method used: rag, search, hybrid, escalation")
    session_id: str = Field(..., description="Session ID")
    escalate: bool = Field(default=False, description="Whether to escalate to human")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Our current savings account rate is 4.5% APY...",
                "sources": [{"source": "rate_sheet.pdf", "type": "internal"}],
                "method": "rag",
                "session_id": "abc-123",
                "escalate": False
            }
        }


class ChatHistory(BaseModel):
    """Chat conversation history"""
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
