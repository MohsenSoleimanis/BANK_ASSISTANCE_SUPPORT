"""
Document chunking strategies
"""
from typing import List, Dict
import re
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentChunker:
    """Chunk documents for optimal RAG retrieval"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """Initialize chunker"""
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Chunk text into overlapping segments"""
        text = self._clean_text(text)
        sentences = self._split_sentences(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append({"text": chunk_text, "metadata": metadata or {}})
                
                # Keep last sentences for overlap
                overlap_sentences = []
                overlap_length = 0
                for s in reversed(current_chunk):
                    s_length = len(s.split())
                    if overlap_length + s_length <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_length += s_length
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_length = overlap_length
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        if current_chunk:
            chunks.append({"text": " ".join(current_chunk), "metadata": metadata or {}})
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?;:\-\'\"()]', '', text)
        return text.strip()
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def chunk_document(self, document: str, source: str, doc_type: str = "policy") -> List[Dict]:
        """Chunk a complete document"""
        metadata = {"source": source, "doc_type": doc_type}
        return self.chunk_text(document, metadata)


# Global chunker instance
chunker = DocumentChunker()
