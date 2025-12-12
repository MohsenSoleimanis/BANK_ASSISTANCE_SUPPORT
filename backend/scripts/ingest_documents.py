"""
Document Ingestion Script
Ingests documents into the vector database
"""
import sys
import os
from pathlib import Path
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.rag.embeddings import embedding_service
from app.core.rag.vector_store import vector_store
from app.core.rag.chunking import chunker
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def ingest_document(file_path: Path, doc_type: str = "policy"):
    """
    Ingest a single document
    
    Args:
        file_path: Path to document
        doc_type: Type of document (policy, form, faq)
    """
    try:
        logger.info(f"Ingesting: {file_path.name}")
        
        # Read document
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Chunk document
        chunks = chunker.chunk_document(
            document=content,
            source=file_path.name,
            doc_type=doc_type
        )
        
        # Generate embeddings
        texts = [chunk["text"] for chunk in chunks]
        embeddings = embedding_service.embed_batch(texts)
        
        # Prepare metadata
        metadata = [chunk["metadata"] for chunk in chunks]
        
        # Add to vector store
        doc_ids = vector_store.add_documents(
            texts=texts,
            embeddings=embeddings,
            metadata=metadata
        )
        
        logger.info(f"✓ Ingested {len(doc_ids)} chunks from {file_path.name}")
        return len(doc_ids)
        
    except Exception as e:
        logger.error(f"Error ingesting {file_path}: {e}")
        return 0


async def ingest_directory(directory: Path, doc_type: str = "policy"):
    """
    Ingest all text files in a directory
    
    Args:
        directory: Directory path
        doc_type: Type of documents
    """
    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        return
    
    # Find all text files
    files = list(directory.glob("*.txt")) + list(directory.glob("*.md"))
    
    if not files:
        logger.warning(f"No text files found in {directory}")
        return
    
    logger.info(f"Found {len(files)} files to ingest")
    
    total_chunks = 0
    for file_path in files:
        chunks = await ingest_document(file_path, doc_type)
        total_chunks += chunks
    
    logger.info(f"\n✅ Ingestion complete! Total chunks: {total_chunks}")


async def main():
    """Main ingestion function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest documents into vector database")
    parser.add_argument("--path", type=str, required=True, help="Path to document or directory")
    parser.add_argument("--type", type=str, default="policy", help="Document type (policy, form, faq)")
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if path.is_file():
        await ingest_document(path, args.type)
    elif path.is_dir():
        await ingest_directory(path, args.type)
    else:
        logger.error(f"Invalid path: {path}")


if __name__ == "__main__":
    asyncio.run(main())
