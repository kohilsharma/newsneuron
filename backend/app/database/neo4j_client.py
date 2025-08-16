"""
Neo4j client for NewsNeuron
Handles knowledge graph operations and relationship queries
"""
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase, Driver, Session
import logging

from app.config import settings


class Neo4jClient:
    """Neo4j client wrapper for NewsNeuron knowledge graph"""
    
    def __init__(self):
        self.driver: Optional[Driver] = None
        self._initialize_driver()
    
    def _initialize_driver(self):
        """Initialize Neo4j driver"""
        try:
            if not settings.neo4j_uri or not settings.neo4j_password:
                print("Warning: Neo4j credentials not configured")
                return
            
            self.driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_username, settings.neo4j_password)
            )
            
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                if result.single():
                    print("Neo4j driver initialized successfully")
                else:
                    raise Exception("Failed to connect to Neo4j")
            
        except Exception as e:
            print(f"Failed to initialize Neo4j driver: {str(e)}")
            self.driver = None
    
    def get_driver(self) -> Optional[Driver]:
        """Get the Neo4j driver instance"""
        return self.driver
    
    def close(self):
        """Close the Neo4j driver"""
        if self.driver:
            self.driver.close()
    
    async def create_entity_node(
        self,
        entity_name: str,
        entity_type: str,
        supabase_id: Optional[int] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an entity node in the knowledge graph
        
        Args:
            entity_name: Name of the entity
            entity_type: Type of entity (PERSON, ORGANIZATION, LOCATION, EVENT)
            supabase_id: Optional Supabase entity ID for linking
            properties: Additional properties for the entity
        
        Returns:
            Created entity node data
        """
        try:
            if not self.driver:
                raise Exception("Neo4j driver not initialized")
            
            props = properties or {}
            props.update({
                "name": entity_name,
                "type": entity_type
            })
            
            if supabase_id:
                props["supabase_id"] = supabase_id
            
            with self.driver.session() as session:
                query = f"""
                MERGE (e:Entity {{name: $name, type: $type}})
                SET e += $properties
                RETURN e
                """
                
                result = session.run(query, name=entity_name, type=entity_type, properties=props)
                record = result.single()
                
                if record:
                    return dict(record["e"])
                else:
                    raise Exception("Failed to create entity node")
                    
        except Exception as e:
            print(f"Error creating entity node: {str(e)}")
            raise
    
    async def create_article_node(
        self,
        supabase_id: int,
        title: str,
        published_date: Optional[str] = None,
        source: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an article node in the knowledge graph
        
        Args:
            supabase_id: Supabase article ID for linking
            title: Article title
            published_date: Publication date (ISO string)
            source: Article source
            properties: Additional properties
        
        Returns:
            Created article node data
        """
        try:
            if not self.driver:
                raise Exception("Neo4j driver not initialized")
            
            props = properties or {}
            props.update({
                "supabase_id": supabase_id,
                "title": title
            })
            
            if published_date:
                props["published_date"] = published_date
            if source:
                props["source"] = source
            
            with self.driver.session() as session:
                query = """
                MERGE (a:Article {supabase_id: $supabase_id})
                SET a += $properties
                RETURN a
                """
                
                result = session.run(query, supabase_id=supabase_id, properties=props)
                record = result.single()
                
                if record:
                    return dict(record["a"])
                else:
                    raise Exception("Failed to create article node")
                    
        except Exception as e:
            print(f"Error creating article node: {str(e)}")
            raise
    
    async def create_relationship(
        self,
        from_node: Dict[str, Any],
        to_node: Dict[str, Any],
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """
        Create a relationship between two nodes
        
        Args:
            from_node: Source node (must have type and identifier)
            to_node: Target node (must have type and identifier)
            relationship_type: Type of relationship (e.g., MENTIONS, WORKS_FOR)
            properties: Additional relationship properties
        """
        try:
            if not self.driver:
                raise Exception("Neo4j driver not initialized")
            
            props = properties or {}
            
            with self.driver.session() as session:
                query = f"""
                MATCH (from:{from_node['type']} {{name: $from_name}})
                MATCH (to:{to_node['type']} {{name: $to_name}})
                MERGE (from)-[r:{relationship_type}]->(to)
                SET r += $properties
                RETURN r
                """
                
                session.run(
                    query,
                    from_name=from_node['name'],
                    to_name=to_node['name'],
                    properties=props
                )
                
        except Exception as e:
            print(f"Error creating relationship: {str(e)}")
            raise
    
    async def get_entity_timeline(
        self,
        entity_name: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get timeline of articles mentioning an entity
        
        Args:
            entity_name: Name of the entity
            limit: Maximum number of articles
        
        Returns:
            List of timeline events (articles) for the entity
        """
        try:
            if not self.driver:
                raise Exception("Neo4j driver not initialized")
            
            with self.driver.session() as session:
                query = """
                MATCH (a:Article)-[:MENTIONS]->(e:Entity)
                WHERE e.name = $entity_name
                RETURN a.title as title, a.published_date as published_date, 
                       a.supabase_id as supabase_id, a.source as source
                ORDER BY a.published_date DESC
                LIMIT $limit
                """
                
                result = session.run(query, entity_name=entity_name, limit=limit)
                
                timeline_events = []
                for record in result:
                    timeline_events.append({
                        "title": record["title"],
                        "published_date": record["published_date"],
                        "supabase_id": record["supabase_id"],
                        "source": record["source"]
                    })
                
                return timeline_events
                
        except Exception as e:
            print(f"Error getting entity timeline: {str(e)}")
            return []
    
    async def get_related_entities(
        self,
        entity_name: str,
        max_depth: int = 2,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get entities related to a given entity through relationships
        
        Args:
            entity_name: Name of the central entity
            max_depth: Maximum relationship depth to traverse
            limit: Maximum number of related entities
        
        Returns:
            List of related entities with relationship information
        """
        try:
            if not self.driver:
                raise Exception("Neo4j driver not initialized")
            
            with self.driver.session() as session:
                query = f"""
                MATCH (start:Entity {{name: $entity_name}})
                MATCH path = (start)-[*1..{max_depth}]-(related:Entity)
                WHERE related.name <> start.name
                RETURN DISTINCT related.name as name, related.type as type,
                       length(path) as distance, count(*) as connection_strength
                ORDER BY connection_strength DESC, distance ASC
                LIMIT $limit
                """
                
                result = session.run(query, entity_name=entity_name, limit=limit)
                
                related_entities = []
                for record in result:
                    related_entities.append({
                        "name": record["name"],
                        "type": record["type"],
                        "distance": record["distance"],
                        "connection_strength": record["connection_strength"]
                    })
                
                return related_entities
                
        except Exception as e:
            print(f"Error getting related entities: {str(e)}")
            return []
    
    async def search_entities_by_name(
        self,
        query: str,
        entity_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search entities by name in the knowledge graph
        
        Args:
            query: Search query
            entity_type: Filter by entity type (optional)
            limit: Maximum number of results
        
        Returns:
            List of matching entities
        """
        try:
            if not self.driver:
                raise Exception("Neo4j driver not initialized")
            
            with self.driver.session() as session:
                base_query = """
                MATCH (e:Entity)
                WHERE toLower(e.name) CONTAINS toLower($query)
                """
                
                if entity_type:
                    base_query += " AND e.type = $entity_type"
                
                base_query += """
                RETURN e.name as name, e.type as type, 
                       size((e)-[:MENTIONS]-()) as mention_count
                ORDER BY mention_count DESC
                LIMIT $limit
                """
                
                params = {"query": query, "limit": limit}
                if entity_type:
                    params["entity_type"] = entity_type
                
                result = session.run(base_query, **params)
                
                entities = []
                for record in result:
                    entities.append({
                        "name": record["name"],
                        "type": record["type"],
                        "mention_count": record["mention_count"]
                    })
                
                return entities
                
        except Exception as e:
            print(f"Error searching entities: {str(e)}")
            return []
    
    async def get_graph_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge graph
        
        Returns:
            Dictionary with graph statistics
        """
        try:
            if not self.driver:
                raise Exception("Neo4j driver not initialized")
            
            with self.driver.session() as session:
                # Count nodes by type
                entity_count = session.run("MATCH (e:Entity) RETURN count(e) as count").single()["count"]
                article_count = session.run("MATCH (a:Article) RETURN count(a) as count").single()["count"]
                
                # Count relationships
                relationship_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
                
                # Get entity type distribution
                entity_types = session.run("""
                MATCH (e:Entity) 
                RETURN e.type as type, count(e) as count 
                ORDER BY count DESC
                """).data()
                
                return {
                    "total_entities": entity_count,
                    "total_articles": article_count,
                    "total_relationships": relationship_count,
                    "entity_types": entity_types
                }
                
        except Exception as e:
            print(f"Error getting graph statistics: {str(e)}")
            return {}


# Global Neo4j client instance
_neo4j_client = None


def get_neo4j_client() -> Neo4jClient:
    """Get singleton Neo4j client instance"""
    global _neo4j_client
    if _neo4j_client is None:
        _neo4j_client = Neo4jClient()
    return _neo4j_client


def get_neo4j_driver() -> Optional[Driver]:
    """Get Neo4j driver directly"""
    client = get_neo4j_client()
    return client.get_driver()
