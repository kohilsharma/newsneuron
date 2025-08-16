"""
Search API endpoints for NewsNeuron
Handles semantic and graph-based search functionality
"""
import time
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query

from app.schemas import SearchRequest, SearchResponse, ArticleResult
from app.dependencies import get_hybrid_retriever, get_current_user
from app.services.hybrid_retriever import HybridRetriever

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def search_articles(
    request: SearchRequest,
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Search articles using hybrid vector-graph approach
    
    Combines semantic similarity search with knowledge graph traversal
    """
    try:
        start_time = time.time()
        
        # Perform hybrid search
        search_results = await retriever.hybrid_search(
            query=request.query,
            search_type=request.search_type,
            limit=request.limit,
            include_entities=request.include_entities
        )
        
        # Convert results to response format
        articles = []
        for result in search_results.get("articles", []):
            article = ArticleResult(
                id=result.get("id"),
                title=result.get("title", ""),
                content=result.get("content", ""),
                url=result.get("url"),
                published_date=result.get("published_date"),
                source=result.get("source"),
                similarity_score=result.get("similarity_score"),
                entities=result.get("entities", [])
            )
            articles.append(article)
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        response = SearchResponse(
            results=articles,
            total_results=len(articles),
            query_entities=search_results.get("query_entities", []),
            search_time_ms=search_time
        )
        
        print(f"Search completed in {search_time:.2f}ms")
        return response
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to perform search: {str(e)}"
        )


@router.get("/", response_model=SearchResponse)
async def search_articles_get(
    q: str = Query(..., description="Search query", min_length=1, max_length=500),
    search_type: str = Query("hybrid", description="Search type: vector, graph, or hybrid"),
    limit: int = Query(10, description="Maximum results", ge=1, le=50),
    include_entities: bool = Query(True, description="Include entity information"),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    GET endpoint for article search (alternative to POST)
    """
    request = SearchRequest(
        query=q,
        search_type=search_type,
        limit=limit,
        include_entities=include_entities
    )
    
    return await search_articles(request, retriever, current_user)


@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., description="Partial query for suggestions", min_length=1),
    limit: int = Query(5, description="Maximum suggestions", ge=1, le=10),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get search suggestions based on partial query
    
    Returns suggestions based on entities and popular search terms
    """
    try:
        # For now, return sample suggestions
        # This will be implemented with proper suggestion logic
        sample_suggestions = [
            f"{query} technology",
            f"{query} news",
            f"{query} analysis",
            f"{query} trends",
            f"{query} impact"
        ]
        
        return {
            "suggestions": sample_suggestions[:limit],
            "query": query,
            "message": "Search suggestions not fully implemented yet"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get search suggestions: {str(e)}"
        )


@router.get("/entities")
async def search_entities(
    query: str = Query(..., description="Entity search query", min_length=1),
    entity_type: str = Query(None, description="Filter by entity type: PERSON, ORGANIZATION, LOCATION, EVENT"),
    limit: int = Query(20, description="Maximum entities", ge=1, le=50),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Search for entities in the knowledge graph
    
    Finds entities that match the query and returns their information
    """
    try:
        start_time = time.time()
        
        # Search for entities
        entities = await retriever.search_entities(
            query=query,
            entity_type=entity_type,
            limit=limit
        )
        
        search_time = (time.time() - start_time) * 1000
        
        return {
            "entities": entities,
            "total_count": len(entities),
            "search_time_ms": search_time,
            "filters": {
                "entity_type": entity_type
            }
        }
        
    except Exception as e:
        print(f"Entity search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search entities: {str(e)}"
        )


@router.get("/similar/{article_id}")
async def find_similar_articles(
    article_id: int,
    limit: int = Query(10, description="Maximum similar articles", ge=1, le=20),
    similarity_threshold: float = Query(0.7, description="Minimum similarity score", ge=0.0, le=1.0),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Find articles similar to a specific article
    
    Uses vector similarity and entity relationships to find related content
    """
    try:
        start_time = time.time()
        
        # Find similar articles
        similar_articles = await retriever.find_similar_articles(
            article_id=article_id,
            limit=limit,
            similarity_threshold=similarity_threshold
        )
        
        search_time = (time.time() - start_time) * 1000
        
        return {
            "article_id": article_id,
            "similar_articles": similar_articles,
            "total_count": len(similar_articles),
            "search_time_ms": search_time,
            "similarity_threshold": similarity_threshold
        }
        
    except Exception as e:
        print(f"Similar articles search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to find similar articles: {str(e)}"
        )
