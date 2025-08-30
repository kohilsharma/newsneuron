"""
Configuration settings for NewsNeuron backend
"""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "NewsNeuron"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API
    api_v1_str: str = "/api/v1"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database - Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    
    # Database - Neo4j
    neo4j_uri: str = ""
    neo4j_username: str = "neo4j"
    neo4j_password: str = ""
    
    # AI Services - OpenRouter for LLM responses (no OpenAI dependency)
    openrouter_api_key: str = ""
    
    # Redis (optional)
    redis_url: str = "redis://localhost:6379"
    
    # Free Local Embedding settings
    use_local_embeddings: bool = True  # Always use free local models
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"  # Free, lightweight model
    embedding_dimension: int = 384  # all-MiniLM-L6-v2 dimensions
    
    # Free embedding model options:
    # - sentence-transformers/all-MiniLM-L6-v2: 384 dimensions (fast, lightweight, default)
    # - sentence-transformers/all-MiniLM-L12-v2: 384 dimensions (slightly better quality)
    # - intfloat/e5-small-v2: 384 dimensions (efficient)
    # - BAAI/bge-small-en-v1.5: 384 dimensions (good performance)
    
    # LLM settings (OpenRouter model slug)
    default_llm_model: str = "deepseek/deepseek-chat-v3.1:free"
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # Search settings
    vector_search_limit: int = 5
    graph_search_max_depth: int = 2
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
