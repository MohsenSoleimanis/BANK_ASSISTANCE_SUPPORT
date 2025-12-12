"""
Hybrid retrieval system
"""
from typing import List, Dict, Optional
from app.core.rag.embeddings import embedding_service
from app.core.rag.vector_store import vector_store
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HybridRetriever:
    """Hybrid retrieval combining vector and keyword search"""
    
    def __init__(self):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.top_k = settings.TOP_K_RESULTS
    
    async def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """Retrieve relevant documents"""
        try:
            top_k = top_k or self.top_k
            logger.info(f"Retrieving documents for: '{query}'")
            
            # Generate query embedding
            query_embedding = self.embedding_service.embed_text(query)
            
            # Vector search
            results = self.vector_store.search(
                query_embedding=query_embedding,
                limit=top_k * 2,
                score_threshold=settings.SIMILARITY_THRESHOLD
            )
            
            if not results:
                return []
            
            # Simple reranking
            results = self._rerank(query, results)
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error retrieving: {e}")
            return []
    
    def _rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
        """Rerank documents"""
        query_terms = set(query.lower().split())
        
        for doc in documents:
            text_lower = doc["text"].lower()
            term_matches = sum(1 for term in query_terms if term in text_lower)
            term_boost = term_matches / len(query_terms) if query_terms else 0
            doc["score"] = doc["score"] * 0.7 + term_boost * 0.3
        
        documents.sort(key=lambda x: x["score"], reverse=True)
        return documents


# Global retriever
retriever = HybridRetriever()
