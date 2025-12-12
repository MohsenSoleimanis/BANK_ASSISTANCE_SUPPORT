"""
Vector database operations using Qdrant
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Optional
from uuid import uuid4
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """Vector database client for document storage"""
    
    def __init__(self):
        """Initialize Qdrant client"""
        self.client = QdrantClient(url=settings.VECTOR_DB_URL)
        self.collection_name = settings.VECTOR_DB_COLLECTION
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if not exists:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            logger.error(f"Error ensuring collection: {e}")
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadata: List[Dict]
    ) -> List[str]:
        """Add documents to vector store"""
        try:
            points = []
            ids = []
            
            for text, embedding, meta in zip(texts, embeddings, metadata):
                doc_id = str(uuid4())
                ids.append(doc_id)
                points.append(
                    PointStruct(
                        id=doc_id,
                        vector=embedding,
                        payload={"text": text, **meta}
                    )
                )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Added {len(points)} documents")
            return ids
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None
    ) -> List[Dict]:
        """Search for similar documents"""
        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=limit,
                score_threshold=score_threshold
            )
            
            documents = []
            for result in results.points:
                doc = {
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "metadata": {k: v for k, v in result.payload.items() if k != "text"}
                }
                documents.append(doc)
            
            logger.info(f"Found {len(documents)} documents")
            return documents
        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []


# Global vector store instance
vector_store = VectorStore()