"""
Query routing logic
"""
from enum import Enum
from typing import Tuple, Dict, Optional
import re
from app.utils.logger import get_logger

logger = get_logger(__name__)


class QueryType(Enum):
    """Types of queries"""
    RAG_ONLY = "rag"
    SEARCH_ONLY = "search"
    HYBRID = "hybrid"
    FORM_FILLING = "form"
    ESCALATE = "escalate"


class QueryRouter:
    """Routes queries to appropriate handlers"""
    
    def __init__(self):
        self.temporal_keywords = ["current", "latest", "today", "2024", "2025", "recent"]
        self.sensitive_keywords = ["password", "pin", "account number", "ssn", "transfer money"]
        self.form_keywords = ["fill out", "application", "apply for", "form"]
    
    async def route(self, query: str, context: Optional[Dict] = None) -> Tuple[QueryType, Dict]:
        """Determine how to handle query"""
        context = context or {}
        query_lower = query.lower()
        
        logger.info(f"Routing query: '{query}'")
        
        # Check form filling mode
        if context.get("active_form"):
            return QueryType.FORM_FILLING, {}
        
        # Check sensitive
        if self._contains_sensitive(query_lower):
            return QueryType.ESCALATE, {"reason": "sensitive_information"}
        
        # Check form request
        if self._is_form_request(query_lower):
            return QueryType.FORM_FILLING, {}
        
        # Check current info needed
        if self._needs_current_info(query_lower):
            return QueryType.SEARCH_ONLY, {}
        
        # Check account specific
        if self._is_account_specific(query_lower):
            return QueryType.ESCALATE, {"reason": "account_access_required"}
        
        # Default to hybrid
        return QueryType.HYBRID, {"confidence": 0.8}
    
    def _contains_sensitive(self, query: str) -> bool:
        return any(kw in query for kw in self.sensitive_keywords)
    
    def _is_form_request(self, query: str) -> bool:
        return any(kw in query for kw in self.form_keywords)
    
    def _needs_current_info(self, query: str) -> bool:
        return any(kw in query for kw in self.temporal_keywords)
    
    def _is_account_specific(self, query: str) -> bool:
        patterns = [r"my account", r"my balance", r"my transactions"]
        return any(re.search(p, query) for p in patterns)


# Global router
query_router = QueryRouter()
