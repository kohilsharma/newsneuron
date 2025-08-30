"""
Hybrid Retriever for NewsNeuron
Combines vector similarity search with knowledge graph traversal
"""
import asyncio
from typing import List, Dict, Any, Optional
from neo4j import Driver

from app.config import settings
from app.database.supabase_client import SupabaseClient
from app.database.neo4j_client import Neo4jClient
from app.services.embedding_service import get_embedding_service


class HybridRetriever:
    """
    Hybrid retriever that combines vector search and graph traversal
    for comprehensive news understanding
    """

    def __init__(self, supabase_client: SupabaseClient, neo4j_driver: Driver):
        self.supabase = supabase_client
        self.neo4j_driver = neo4j_driver
        self.neo4j_client = Neo4jClient()
        self.embedding_service = get_embedding_service()

    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text using available embedding service
        
        Args:
            text: Input text to embed
        
        Returns:
            List of embedding values or None if no backend available
        """
        try:
            embedding = await self.embedding_service.generate_embedding(text)
            if embedding:
                backend_info = self.embedding_service.get_backend_info()
                print(f"Generated {backend_info['backend']} embedding with {len(embedding)} dimensions (model: {backend_info['model']})")
            else:
                print("No embedding generated - no backend available")
            return embedding

        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return None

    async def vector_search(
        self,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.3  # Lowered for sentence-transformers
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
            
            # If no embedding was generated, return empty results
            if query_embedding is None:
                print("No embedding available for vector search. Returning empty results.")
                return []

            # Prefer chunk-level search for better recall
            chunk_matches = await self.supabase.search_chunks_by_similarity(
                query_embedding=query_embedding,
                limit=limit * 2,
                similarity_threshold=max(0.1, similarity_threshold * 0.5)  # Auto-adjust for sentence-transformers
            )

            articles: List[Dict[str, Any]] = []
            seen_ids = set()
            for match in chunk_matches:
                article_id = match.get("article_id")
                if not article_id or article_id in seen_ids:
                    continue
                article = await self.supabase.get_article_by_id(article_id)
                if article:
                    # include snippet from chunk
                    article["similarity_score"] = match.get("similarity")
                    article["snippet"] = match.get("content")
                    articles.append(article)
                    seen_ids.add(article_id)
                if len(articles) >= limit:
                    break

            return articles

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
            "Google", "Microsoft", "Tesla", "Apple", "Meta"
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
                    similarity_threshold=0.2  # Lowered for sentence-transformers
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
        similarity_threshold: float = 0.3  # Lowered for sentence-transformers
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

    def synthesize_results(
        self,
        vector_results: List[Dict[str, Any]],
        graph_results: List[Dict[str, Any]],
    ) -> str:
        """
        Produce a compact textual context from vector and graph results
        suitable for conditioning an LLM.
        """
        lines: List[str] = []
        if vector_results:
            lines.append("Relevant Articles:")
            for i, art in enumerate(vector_results[:5], 1):
                title = art.get("title", "Unknown")
                source = art.get("source", "")
                sim = art.get("similarity_score")
                sim_part = f" (sim {sim:.2f})" if isinstance(sim, (int, float)) else ""
                lines.append(f"{i}. {title}{sim_part} - {source}")
                snippet = art.get("snippet") or art.get("content", "")
                if snippet:
                    snippet_str = snippet[:200] + ("..." if len(snippet) > 200 else "")
                    lines.append(f"   Snippet: {snippet_str}")
        if graph_results:
            lines.append("\nEntity Relationships:")
            for g in graph_results[:3]:
                ent = g.get("entity", "")
                related = ", ".join([r.get("name", "") for r in g.get("related_entities", [])[:3]])
                if ent and related:
                    lines.append(f"- {ent}: {related}")
        return "\n".join(lines) if lines else "Context: no additional results."
