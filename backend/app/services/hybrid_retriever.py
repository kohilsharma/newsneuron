"""
Hybrid Retriever for NewsNeuron
Combines vector similarity search with knowledge graph traversal
"""
import asyncio
from typing import List, Dict, Any, Optional
import openai
from neo4j import Driver

from app.config import settings
from app.database.supabase_client import SupabaseClient
from app.database.neo4j_client import Neo4jClient


class HybridRetriever:
    """
    Hybrid retriever that combines vector search and graph traversal
    for comprehensive news understanding
    """
    
    def __init__(self, supabase_client: SupabaseClient, neo4j_driver: Driver):
        self.supabase = supabase_client
        self.neo4j_driver = neo4j_driver
        self.neo4j_client = Neo4jClient()
        self._setup_openai()
    
    def _setup_openai(self):
        """Setup OpenAI client for embeddings"""
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        else:
            print("Warning: OpenAI API key not configured")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text using OpenAI
        
        Args:
            text: Input text to embed
        
        Returns:
            List of embedding values
        """
        try:
            if not settings.openai_api_key:
                # Return dummy embedding for development
                return [0.0] * settings.embedding_dimension
            
            response = await openai.Embedding.acreate(
                model=settings.embedding_model,
                input=text
            )
            
            return response['data'][0]['embedding']
            
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            # Return dummy embedding on error
            return [0.0] * settings.embedding_dimension
    
    async def vector_search(
        self,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search in Supabase
        
        Args:
            query: Search query
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score
        
        Returns:
            List of similar articles with scores
        """
        try:
            # Generate embedding for query
            query_embedding = await self.generate_embedding(query)
            
            # Search for similar articles
            results = await self.supabase.search_articles_by_similarity(
                query_embedding=query_embedding,
                limit=limit,
                similarity_threshold=similarity_threshold
            )
            
            return results
            
        except Exception as e:
            print(f"Error in vector search: {str(e)}")
            return []
    
    async def graph_search(
        self,
        entities: List[str],
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Perform graph traversal search in Neo4j
        
        Args:
            entities: List of entity names to search for
            max_depth: Maximum relationship depth to traverse
        
        Returns:
            List of related articles and entities
        """
        try:
            if not entities:
                return []
            
            graph_results = []
            
            for entity in entities:
                # Get entity timeline
                timeline = await self.neo4j_client.get_entity_timeline(
                    entity_name=entity,
                    limit=10
                )
                
                # Get related entities
                related = await self.neo4j_client.get_related_entities(
                    entity_name=entity,
                    max_depth=max_depth,
                    limit=10
                )
                
                graph_results.append({
                    "entity": entity,
                    "timeline": timeline,
                    "related_entities": related
                })
            
            return graph_results
            
        except Exception as e:
            print(f"Error in graph search: {str(e)}")
            return []
    
    def extract_entities(self, text: str) -> List[str]:
        """
        Extract entities from text (placeholder implementation)
        
        Args:
            text: Input text to analyze
        
        Returns:
            List of extracted entity names
        """
        # TODO: Implement proper NER with spaCy
        # For now, return some common entity types from the text
        common_entities = [
            "AI", "Technology", "Climate", "Politics", "Economy",
            "OpenAI", "Google", "Microsoft", "Tesla", "Apple"
        ]
        
        entities = []
        text_lower = text.lower()
        
        for entity in common_entities:
            if entity.lower() in text_lower:
                entities.append(entity)
        
        return entities[:5]  # Limit to 5 entities
    
    async def hybrid_search(
        self,
        query: str,
        search_type: str = "hybrid",
        limit: int = 10,
        include_entities: bool = True
    ) -> Dict[str, Any]:
        """
        Perform hybrid search combining vector and graph approaches
        
        Args:
            query: Search query
            search_type: Type of search ("vector", "graph", or "hybrid")
            limit: Maximum number of results
            include_entities: Whether to include entity information
        
        Returns:
            Combined search results with articles and entities
        """
        try:
            results = {
                "articles": [],
                "query_entities": [],
                "graph_results": []
            }
            
            # Extract entities from query
            query_entities = self.extract_entities(query) if include_entities else []
            results["query_entities"] = query_entities
            
            if search_type in ["vector", "hybrid"]:
                # Perform vector search
                vector_results = await self.vector_search(
                    query=query,
                    limit=limit,
                    similarity_threshold=0.6
                )
                results["articles"].extend(vector_results)
            
            if search_type in ["graph", "hybrid"] and query_entities:
                # Perform graph search
                graph_results = await self.graph_search(
                    entities=query_entities,
                    max_depth=2
                )
                results["graph_results"] = graph_results
                
                # Add articles from graph results
                for graph_result in graph_results:
                    for timeline_event in graph_result.get("timeline", []):
                        if timeline_event.get("supabase_id"):
                            # Get full article from Supabase
                            article = await self.supabase.get_article_by_id(
                                timeline_event["supabase_id"]
                            )
                            if article:
                                article["from_graph"] = True
                                results["articles"].append(article)
            
            # Remove duplicates and limit results
            seen_ids = set()
            unique_articles = []
            
            for article in results["articles"]:
                article_id = article.get("id")
                if article_id and article_id not in seen_ids:
                    seen_ids.add(article_id)
                    unique_articles.append(article)
            
            results["articles"] = unique_articles[:limit]
            
            return results
            
        except Exception as e:
            print(f"Error in hybrid search: {str(e)}")
            return {
                "articles": [],
                "query_entities": [],
                "graph_results": []
            }
    
    async def search_entities(
        self,
        query: str,
        entity_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for entities across both databases
        
        Args:
            query: Entity search query
            entity_type: Filter by entity type
            limit: Maximum number of results
        
        Returns:
            List of matching entities
        """
        try:
            # Search in both databases concurrently
            supabase_task = self.supabase.search_entities(query, entity_type, limit)
            neo4j_task = self.neo4j_client.search_entities_by_name(query, entity_type, limit)
            
            supabase_entities, neo4j_entities = await asyncio.gather(
                supabase_task, neo4j_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(supabase_entities, Exception):
                supabase_entities = []
            if isinstance(neo4j_entities, Exception):
                neo4j_entities = []
            
            # Combine and deduplicate results
            all_entities = []
            seen_names = set()
            
            for entity in supabase_entities + neo4j_entities:
                name = entity.get("name")
                if name and name not in seen_names:
                    seen_names.add(name)
                    all_entities.append(entity)
            
            return all_entities[:limit]
            
        except Exception as e:
            print(f"Error searching entities: {str(e)}")
            return []
    
    async def find_similar_articles(
        self,
        article_id: int,
        limit: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find articles similar to a given article
        
        Args:
            article_id: ID of the reference article
            limit: Maximum number of similar articles
            similarity_threshold: Minimum similarity score
        
        Returns:
            List of similar articles
        """
        try:
            # Get the reference article
            reference_article = await self.supabase.get_article_by_id(article_id)
            
            if not reference_article:
                return []
            
            # Use article content for similarity search
            content = reference_article.get("content", "")
            title = reference_article.get("title", "")
            search_text = f"{title} {content}"
            
            # Perform vector search
            similar_articles = await self.vector_search(
                query=search_text,
                limit=limit + 1,  # +1 to exclude self
                similarity_threshold=similarity_threshold
            )
            
            # Remove the reference article from results
            filtered_articles = [
                article for article in similar_articles
                if article.get("id") != article_id
            ]
            
            return filtered_articles[:limit]
            
        except Exception as e:
            print(f"Error finding similar articles: {str(e)}")
            return []
    
    async def get_related_entities(
        self,
        entity_name: str,
        max_depth: int = 2,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get entities related to a given entity
        
        Args:
            entity_name: Name of the central entity
            max_depth: Maximum relationship depth
            limit: Maximum number of related entities
        
        Returns:
            List of related entities
        """
        try:
            return await self.neo4j_client.get_related_entities(
                entity_name=entity_name,
                max_depth=max_depth,
                limit=limit
            )
        except Exception as e:
            print(f"Error getting related entities: {str(e)}")
            return []
