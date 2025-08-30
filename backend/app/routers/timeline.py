"""
Timeline API endpoints for NewsNeuron
Handles entity timeline visualization and story evolution tracking
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query

from app.schemas import TimelineRequest, TimelineResponse, TimelineEvent
from app.dependencies import get_hybrid_retriever
from app.services.hybrid_retriever import HybridRetriever
from app.services.timeline_generator import TimelineGenerator

router = APIRouter()


@router.post("/", response_model=TimelineResponse)
async def generate_timeline(
    request: TimelineRequest,
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
):
    """
    Generate timeline for a specific entity
    
    Creates chronological visualization of entity mentions and story evolution
    """
    try:
        start_time = time.time()
        
        # Initialize timeline generator
        generator = TimelineGenerator(retriever)
        
        # Generate timeline
        timeline_data = await generator.generate_timeline(
            entity_name=request.entity_name,
            start_date=request.start_date,
            end_date=request.end_date,
            limit=request.limit,
        )
        
        # Convert events to response format
        events = []
        for event_data in timeline_data.get("events", []):
            event = TimelineEvent(
                id=event_data.get("id"),
                title=event_data.get("title", ""),
                date=event_data.get("date"),
                description=event_data.get("description", ""),
                article_url=event_data.get("article_url"),
                source=event_data.get("source"),
                entity_role=event_data.get("entity_role"),
                related_entities=event_data.get("related_entities", [])
            )
            events.append(event)
        
        response = TimelineResponse(
            entity_name=request.entity_name,
            events=events,
            total_events=len(events),
            date_range=timeline_data.get("date_range", {})
        )
        
        processing_time = time.time() - start_time
        print(f"Timeline generation time: {processing_time:.2f}s")
        
        return response
        
    except Exception as e:
        print(f"Timeline generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate timeline: {str(e)}"
        )


@router.get("/{entity_name}", response_model=TimelineResponse)
async def get_entity_timeline(
    entity_name: str,
    start_date: Optional[datetime] = Query(None, description="Timeline start date"),
    end_date: Optional[datetime] = Query(None, description="Timeline end date"),
    limit: int = Query(50, description="Maximum timeline events", ge=1, le=100),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
):
    """
    GET endpoint for entity timeline (alternative to POST)
    """
    request = TimelineRequest(
        entity_name=entity_name,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    
    return await generate_timeline(request, retriever)


@router.get("/{entity_name}/summary")
async def get_timeline_summary(
    entity_name: str,
    days_back: int = Query(30, description="Days to look back", ge=1, le=365),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
):
    """
    Get a summary of entity timeline activity
    
    Provides overview statistics and key events for the entity
    """
    try:
        start_time = time.time()
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Get timeline summary
        generator = TimelineGenerator(retriever)
        summary = await generator.get_timeline_summary(
            entity_name=entity_name,
            start_date=start_date,
            end_date=end_date
        )
        
        processing_time = time.time() - start_time
        
        return {
            "entity_name": entity_name,
            "time_period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": days_back
            },
            "summary": summary,
            "processing_time_ms": processing_time * 1000
        }
        
    except Exception as e:
        print(f"Timeline summary error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get timeline summary: {str(e)}"
        )


@router.get("/{entity_name}/related")
async def get_related_entities_timeline(
    entity_name: str,
    max_depth: int = Query(2, description="Maximum relationship depth", ge=1, le=3),
    limit: int = Query(20, description="Maximum related entities", ge=1, le=50),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
):
    """
    Get timeline information for entities related to the specified entity
    
    Finds connected entities and their timeline activity
    """
    try:
        start_time = time.time()
        
        # Get related entities
        related_entities = await retriever.get_related_entities(
            entity_name=entity_name,
            max_depth=max_depth,
            limit=limit
        )
        
        # For now, return basic related entity information
        # Timeline integration for related entities will be implemented later
        
        processing_time = time.time() - start_time
        
        return {
            "entity_name": entity_name,
            "related_entities": related_entities,
            "total_count": len(related_entities),
            "max_depth": max_depth,
            "processing_time_ms": processing_time * 1000,
            "message": "Related entity timeline integration not fully implemented yet"
        }
        
    except Exception as e:
        print(f"Related entities timeline error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get related entities timeline: {str(e)}"
        )


@router.get("/events/trending")
async def get_trending_events(
    days_back: int = Query(7, description="Days to analyze", ge=1, le=30),
    limit: int = Query(10, description="Maximum trending events", ge=1, le=20),
):
    """
    Get trending events across all timelines
    
    Identifies events with high activity or rapid development
    """
    try:
        # For now, return sample trending events
        # This will be implemented with proper trend analysis
        sample_events = [
            {
                "event_name": "AI Technology Summit",
                "entity_count": 15,
                "mention_count": 45,
                "trend_score": 0.92,
                "time_range": {
                    "start": datetime.now() - timedelta(days=2),
                    "end": datetime.now()
                }
            },
            {
                "event_name": "Climate Policy Changes",
                "entity_count": 8,
                "mention_count": 32,
                "trend_score": 0.78,
                "time_range": {
                    "start": datetime.now() - timedelta(days=5),
                    "end": datetime.now() - timedelta(days=1)
                }
            }
        ]
        
        return {
            "trending_events": sample_events[:limit],
            "time_period_days": days_back,
            "message": "Trending events analysis not fully implemented yet"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get trending events: {str(e)}"
        )
