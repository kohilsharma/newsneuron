"""
Flashcards API endpoints for NewsNeuron
Handles AI-generated flashcard summaries of news
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query

from app.schemas import FlashcardRequest, FlashcardResponse, Flashcard
from app.dependencies import get_hybrid_retriever
from app.services.hybrid_retriever import HybridRetriever
from app.services.flashcard_generator import FlashcardGenerator

router = APIRouter()


@router.post("/", response_model=FlashcardResponse)
async def generate_flashcards(
    request: FlashcardRequest,
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
):
    """
    Generate AI-summarized flashcards from recent news
    
    Creates concise, digestible news summaries with key points and entities
    """
    try:
        start_time = time.time()
        
        # Initialize flashcard generator
        generator = FlashcardGenerator(retriever)
        
        # Generate flashcards based on request parameters
        flashcards = await generator.generate_flashcards(
            topics=request.topics,
            date_range=request.date_range,
            limit=request.limit,
        )
        
        response = FlashcardResponse(
            flashcards=flashcards,
            total_count=len(flashcards)
        )
        
        processing_time = time.time() - start_time
        print(f"Flashcard generation time: {processing_time:.2f}s")
        
        return response
        
    except Exception as e:
        print(f"Flashcard generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate flashcards: {str(e)}"
        )


@router.get("/", response_model=FlashcardResponse)
async def get_recent_flashcards(
    limit: int = Query(10, description="Number of flashcards to retrieve", ge=1, le=20),
    topics: List[str] = Query(None, description="Filter by topics"),
    days_back: int = Query(7, description="How many days back to look", ge=1, le=30),
    retriever: HybridRetriever = Depends(get_hybrid_retriever),
):
    """
    Get recently generated flashcards
    
    Retrieves pre-generated flashcards from the specified time period
    """
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        date_range = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        # Create request object
        request = FlashcardRequest(
            topics=topics,
            date_range=date_range,
            limit=limit
        )
        
        # Generate flashcards
        generator = FlashcardGenerator(retriever)
        flashcards = await generator.generate_flashcards(
            topics=request.topics,
            date_range=request.date_range,
            limit=request.limit,
        )
        
        return FlashcardResponse(
            flashcards=flashcards,
            total_count=len(flashcards)
        )
        
    except Exception as e:
        print(f"Recent flashcards error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve recent flashcards: {str(e)}"
        )


@router.get("/{flashcard_id}")
async def get_flashcard_details(
    flashcard_id: str,
):
    """
    Get detailed information about a specific flashcard
    TODO: Implement flashcard storage and retrieval
    """
    try:
        # For now, return a sample flashcard
        # This will be implemented when flashcard storage is added
        sample_flashcard = {
            "id": flashcard_id,
            "title": "Sample Flashcard",
            "summary": "This is a sample flashcard summary",
            "key_points": [
                "Sample key point 1",
                "Sample key point 2",
                "Sample key point 3"
            ],
            "entities": [],
            "source_articles": [],
            "created_at": datetime.now(),
            "category": "sample"
        }
        
        return {
            "flashcard": sample_flashcard,
            "message": "Flashcard details retrieval not fully implemented yet"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve flashcard details: {str(e)}"
        )


@router.get("/topics/trending")
async def get_trending_topics(
    limit: int = Query(10, description="Number of trending topics", ge=1, le=20),
    days_back: int = Query(7, description="Time period for trending analysis", ge=1, le=30),
):
    """
    Get trending topics for flashcard generation
    
    Analyzes recent news to identify trending topics and entities
    """
    try:
        # For now, return sample trending topics
        # This will be implemented with proper trend analysis
        sample_topics = [
            {"topic": "Artificial Intelligence", "mention_count": 45, "trend_score": 0.85},
            {"topic": "Climate Change", "mention_count": 38, "trend_score": 0.72},
            {"topic": "Technology", "mention_count": 52, "trend_score": 0.68},
            {"topic": "Politics", "mention_count": 41, "trend_score": 0.65},
            {"topic": "Economy", "mention_count": 33, "trend_score": 0.58}
        ]
        
        return {
            "trending_topics": sample_topics[:limit],
            "time_period_days": days_back,
            "message": "Trending topics analysis not fully implemented yet"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get trending topics: {str(e)}"
        )
