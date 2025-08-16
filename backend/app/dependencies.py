"""
Dependency injection for FastAPI endpoints
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database.supabase_client import get_supabase_client
from app.database.neo4j_client import get_neo4j_driver
from app.services.langgraph_agent import LangGraphAgent
from app.services.hybrid_retriever import HybridRetriever

# Security
security = HTTPBearer(auto_error=False)


def get_supabase():
    """Get Supabase client dependency"""
    return get_supabase_client()


def get_neo4j():
    """Get Neo4j driver dependency"""
    return get_neo4j_driver()


def get_hybrid_retriever(
    supabase=Depends(get_supabase),
    neo4j_driver=Depends(get_neo4j)
) -> HybridRetriever:
    """Get hybrid retriever dependency"""
    return HybridRetriever(supabase, neo4j_driver)


def get_langgraph_agent(
    retriever: HybridRetriever = Depends(get_hybrid_retriever)
) -> LangGraphAgent:
    """Get LangGraph agent dependency"""
    return LangGraphAgent(retriever)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Get current user from token (optional for now)
    TODO: Implement proper authentication when user system is ready
    """
    # For now, return a dummy user or None
    # This can be extended later when user authentication is implemented
    if credentials:
        # Validate token here
        pass
    return {"id": "anonymous", "role": "user"}


def validate_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Validate API key for protected endpoints
    TODO: Implement when API key system is ready
    """
    # For development, skip validation
    # In production, validate the API key
    return True
