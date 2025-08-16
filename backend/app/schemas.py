"""
Pydantic schemas for API request/response models
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Base schemas
class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: str = ""


# Chat schemas
class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str = Field(..., description="User message", min_length=1, max_length=1000)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    use_hybrid_search: bool = Field(True, description="Enable hybrid vector-graph search")


class ChatResponse(BaseResponse):
    """Chat response model"""
    response: str = Field(..., description="AI assistant response")
    conversation_id: str = Field(..., description="Conversation ID")
    sources: List[Dict[str, Any]] = Field(default=[], description="Source articles used")
    entities_mentioned: List[str] = Field(default=[], description="Entities mentioned in response")


# Search schemas
class SearchRequest(BaseModel):
    """Search request model"""
    query: str = Field(..., description="Search query", min_length=1, max_length=500)
    search_type: str = Field("hybrid", description="Search type: 'vector', 'graph', or 'hybrid'")
    limit: int = Field(10, description="Maximum number of results", ge=1, le=50)
    include_entities: bool = Field(True, description="Include entity information")


class ArticleResult(BaseModel):
    """Article search result model"""
    id: int
    title: str
    content: str
    url: Optional[str] = None
    published_date: Optional[datetime] = None
    source: Optional[str] = None
    similarity_score: Optional[float] = None
    entities: List[Dict[str, str]] = Field(default=[])


class SearchResponse(BaseResponse):
    """Search response model"""
    results: List[ArticleResult]
    total_results: int
    query_entities: List[str] = Field(default=[])
    search_time_ms: float


# Flashcard schemas
class FlashcardRequest(BaseModel):
    """Flashcard request model"""
    topics: Optional[List[str]] = Field(None, description="Specific topics to filter by")
    date_range: Optional[Dict[str, str]] = Field(None, description="Date range filter")
    limit: int = Field(10, description="Number of flashcards", ge=1, le=20)


class Flashcard(BaseModel):
    """Flashcard model"""
    id: str
    title: str = Field(..., description="Flashcard title")
    summary: str = Field(..., description="Brief summary")
    key_points: List[str] = Field(..., description="Key points")
    entities: List[Dict[str, str]] = Field(default=[], description="Related entities")
    source_articles: List[Dict[str, Any]] = Field(default=[], description="Source articles")
    created_at: datetime
    category: Optional[str] = None


class FlashcardResponse(BaseResponse):
    """Flashcard response model"""
    flashcards: List[Flashcard]
    total_count: int


# Timeline schemas
class TimelineRequest(BaseModel):
    """Timeline request model"""
    entity_name: str = Field(..., description="Entity name for timeline", min_length=1)
    start_date: Optional[datetime] = Field(None, description="Timeline start date")
    end_date: Optional[datetime] = Field(None, description="Timeline end date")
    limit: int = Field(50, description="Maximum timeline events", ge=1, le=100)


class TimelineEvent(BaseModel):
    """Timeline event model"""
    id: int
    title: str
    date: datetime
    description: str
    article_url: Optional[str] = None
    source: Optional[str] = None
    entity_role: Optional[str] = None
    related_entities: List[str] = Field(default=[])


class TimelineResponse(BaseResponse):
    """Timeline response model"""
    entity_name: str
    events: List[TimelineEvent]
    total_events: int
    date_range: Dict[str, datetime]


# Entity schemas
class Entity(BaseModel):
    """Entity model"""
    id: int
    name: str
    type: str  # PERSON, ORGANIZATION, LOCATION, EVENT
    mentions_count: int = 0
    first_mentioned: Optional[datetime] = None
    last_mentioned: Optional[datetime] = None


class EntityResponse(BaseResponse):
    """Entity response model"""
    entities: List[Entity]
    total_count: int


# Error schemas
class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# Health check schema
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    app_name: str
    version: str
    databases: Dict[str, str]
