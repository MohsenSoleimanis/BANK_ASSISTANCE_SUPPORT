"""
Application configuration management
Loads environment variables and provides settings throughout the app
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Settings
    APP_NAME: str = "Bank Support AI"
    ENV: str = "development"
    DEBUG: bool = True
    
    # API Keys
    GROQ_API_KEY: str
    TAVILY_API_KEY: str
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/bankdb"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Vector Database
    VECTOR_DB_URL: str = "http://localhost:6333"
    VECTOR_DB_COLLECTION: str = "bank_documents"
    
    # Embedding Model
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # RAG Settings
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    TOP_K_RESULTS: int = 5
    RERANK_TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    # LLM Settings
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    MAX_TOKENS: int = 2000
    TEMPERATURE: float = 0.7
    
    # Search Settings
    TAVILY_MAX_RESULTS: int = 5
    SEARCH_CACHE_TTL: int = 3600  # 1 hour
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Using lru_cache ensures we only load settings once
    """
    return Settings()


# Global settings instance
settings = get_settings()
