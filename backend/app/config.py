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
    
    # AI Services
    openai_api_key: str = ""
    openrouter_api_key: str = ""
    
    # Security
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Redis (optional)
    redis_url: str = "redis://localhost:6379"
    
    # Embedding settings
    embedding_model: str = "text-embedding-ada-002"
    embedding_dimension: int = 1536
    
    # LLM settings
    default_llm_model: str = "openai/gpt-4-turbo-preview"
    max_tokens: int = 2000
    temperature: float = 0.7
    
    # Search settings
    vector_search_limit: int = 5
    graph_search_max_depth: int = 2
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
