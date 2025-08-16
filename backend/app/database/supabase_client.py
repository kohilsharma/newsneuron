"""
Supabase client for NewsNeuron
Handles vector database operations with pgvector
"""
import os
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
import numpy as np

from app.config import settings


class SupabaseClient:
    """Supabase client wrapper for NewsNeuron"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Supabase client"""
        try:
            if not settings.supabase_url or not settings.supabase_anon_key:
                print("Warning: Supabase credentials not configured")
                return
            
            self.client = create_client(
                settings.supabase_url,
                settings.supabase_anon_key
            )
            print("Supabase client initialized successfully")
            
        except Exception as e:
            print(f"Failed to initialize Supabase client: {str(e)}")
            self.client = None
    
    def get_client(self) -> Optional[Client]:
        """Get the Supabase client instance"""
        return self.client
    
    async def insert_article(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert an article into the database
        
        Args:
            article_data: Dictionary containing article information
                - title: str
                - content: str
                - url: str (optional)
                - published_date: datetime (optional)
                - source: str (optional)
                - embedding: List[float] (optional)
        
        Returns:
            Dictionary with inserted article data including ID
        """
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            response = self.client.table("articles").insert(article_data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise Exception("Failed to insert article")
                
        except Exception as e:
            print(f"Error inserting article: {str(e)}")
            raise
    
    async def search_articles_by_similarity(
        self,
        query_embedding: List[float],
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search articles using vector similarity
        
        Args:
            query_embedding: Query vector for similarity search
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
        
        Returns:
            List of similar articles with similarity scores
        """
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            # Convert embedding to string format for pgvector
            embedding_str = f"[{','.join(map(str, query_embedding))}]"
            
            # Perform similarity search using pgvector
            response = self.client.rpc(
                "match_articles",
                {
                    "query_embedding": embedding_str,
                    "match_threshold": similarity_threshold,
                    "match_count": limit
                }
            ).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error in similarity search: {str(e)}")
            return []
    
    async def get_article_by_id(self, article_id: int) -> Optional[Dict[str, Any]]:
        """
        Get article by ID
        
        Args:
            article_id: Article ID
        
        Returns:
            Article data or None if not found
        """
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            response = self.client.table("articles").select("*").eq("id", article_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"Error getting article by ID: {str(e)}")
            return None
    
    async def get_articles_by_entity(
        self,
        entity_name: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get articles that mention a specific entity
        
        Args:
            entity_name: Name of the entity
            limit: Maximum number of articles
        
        Returns:
            List of articles mentioning the entity
        """
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            # Query articles through entity relationship
            response = self.client.table("articles") \
                .select("*, article_entities!inner(entity_id), entities!article_entities(name)") \
                .eq("entities.name", entity_name) \
                .limit(limit) \
                .execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error getting articles by entity: {str(e)}")
            return []
    
    async def insert_entity(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert an entity into the database
        
        Args:
            entity_data: Dictionary containing entity information
                - name: str
                - type: str (PERSON, ORGANIZATION, LOCATION, EVENT)
        
        Returns:
            Dictionary with inserted entity data including ID
        """
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            response = self.client.table("entities").insert(entity_data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise Exception("Failed to insert entity")
                
        except Exception as e:
            print(f"Error inserting entity: {str(e)}")
            raise
    
    async def link_article_entity(self, article_id: int, entity_id: int):
        """
        Create a link between an article and an entity
        
        Args:
            article_id: Article ID
            entity_id: Entity ID
        """
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            link_data = {
                "article_id": article_id,
                "entity_id": entity_id
            }
            
            response = self.client.table("article_entities").insert(link_data).execute()
            
            if not response.data:
                raise Exception("Failed to link article and entity")
                
        except Exception as e:
            print(f"Error linking article and entity: {str(e)}")
            raise
    
    async def search_entities(
        self,
        query: str,
        entity_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search entities by name
        
        Args:
            query: Search query
            entity_type: Filter by entity type (optional)
            limit: Maximum number of results
        
        Returns:
            List of matching entities
        """
        try:
            if not self.client:
                raise Exception("Supabase client not initialized")
            
            query_builder = self.client.table("entities").select("*")
            
            # Add text search
            query_builder = query_builder.ilike("name", f"%{query}%")
            
            # Add type filter if specified
            if entity_type:
                query_builder = query_builder.eq("type", entity_type)
            
            response = query_builder.limit(limit).execute()
            
            return response.data if response.data else []
            
        except Exception as e:
            print(f"Error searching entities: {str(e)}")
            return []


# Global Supabase client instance
_supabase_client = None


def get_supabase_client() -> SupabaseClient:
    """Get singleton Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
