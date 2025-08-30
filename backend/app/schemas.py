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


# Enhanced Chat schemas with interactive features
class ChatMessage(BaseModel):
    """Chat message model with enhanced metadata"""
    id: str = Field(default_factory=lambda: f"msg_{int(datetime.now().timestamp() * 1000)}")
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Message metadata")
    sources: Optional[List[Dict[str, Any]]] = Field(default=[], description="Sources for this message")
    citations: Optional[List[Dict[str, Any]]] = Field(default=[], description="Parsed citations")
    typing_animation: Optional[bool] = Field(default=False, description="Show typing animation")


class CitationInfo(BaseModel):
    """Citation information with linking capabilities"""
    id: str = Field(..., description="Citation ID")
    source_name: str = Field(..., description="Source name as it appears in text")
    title: str = Field(..., description="Full article title")
    url: Optional[str] = Field(None, description="Article URL")
    publication: str = Field(..., description="Publication source")
    published_date: Optional[str] = Field(None, description="Publication date")
    snippet: Optional[str] = Field(None, description="Relevant snippet")
    similarity_score: Optional[float] = Field(None, description="Relevance score")
    position_in_text: Dict[str, int] = Field(..., description="Start and end positions in response")
    verification_url: Optional[str] = Field(None, description="URL for verification")


class ChatRequest(BaseModel):
    """Enhanced chat request model"""
    message: str = Field(..., description="User message", min_length=1, max_length=2000)
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    use_hybrid_search: bool = Field(True, description="Enable hybrid vector-graph search")
    include_citations: bool = Field(True, description="Include detailed citation information")
    response_style: str = Field("balanced", description="Response style: concise, balanced, detailed")
    user_preferences: Optional[Dict[str, Any]] = Field(default={}, description="User preferences")


class TypingStatus(BaseModel):
    """Typing status for real-time updates"""
    conversation_id: str = Field(..., description="Conversation ID")
    is_typing: bool = Field(..., description="Whether AI is typing")
    stage: str = Field("", description="Current processing stage")
    estimated_time: Optional[int] = Field(None, description="Estimated completion time in seconds")


class ChatResponse(BaseResponse):
    """Enhanced chat response model with interactive features"""
    response: str = Field(..., description="AI assistant response")
    conversation_id: str = Field(..., description="Conversation ID")
    message_id: str = Field(..., description="Unique message ID")
    sources: List[Dict[str, Any]] = Field(default=[], description="Source articles used")
    citations: List[CitationInfo] = Field(default=[], description="Detailed citation information")
    entities_mentioned: List[str] = Field(default=[], description="Entities mentioned in response")
    rag_quality: Dict[str, Any] = Field(default={}, description="RAG quality metrics")
    processing_time: float = Field(..., description="Response processing time")
    suggested_questions: List[str] = Field(default=[], description="Suggested follow-up questions")
    response_metadata: Dict[str, Any] = Field(default={}, description="Response metadata")
    interactive_elements: List[Dict[str, Any]] = Field(default=[], description="Interactive UI elements")


class ConversationSummary(BaseModel):
    """Conversation summary model"""
    conversation_id: str = Field(..., description="Conversation ID")
    title: str = Field(..., description="Auto-generated conversation title")
    message_count: int = Field(..., description="Number of messages")
    last_updated: datetime = Field(..., description="Last message timestamp")
    topics_discussed: List[str] = Field(default=[], description="Main topics discussed")
    key_insights: List[str] = Field(default=[], description="Key insights from conversation")
    mood: str = Field("neutral", description="Conversation mood/tone")


class ChatSettings(BaseModel):
    """User chat settings and preferences"""
    theme: str = Field("auto", description="Chat theme: light, dark, auto")
    animation_speed: str = Field("normal", description="Animation speed: slow, normal, fast")
    citation_style: str = Field("inline", description="Citation style: inline, footnotes, sidebar")
    auto_suggest: bool = Field(True, description="Enable auto-suggestions")
    sound_effects: bool = Field(True, description="Enable sound effects")
    compact_mode: bool = Field(False, description="Compact message display")
    show_timestamps: bool = Field(True, description="Show message timestamps")
    show_sources: bool = Field(True, description="Show source information")


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
