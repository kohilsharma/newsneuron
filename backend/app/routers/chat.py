"""
Enhanced Interactive Chat API for NewsNeuron
Handles AI chatbot interactions with citation linking and real-time features
"""
import uuid
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect

from app.schemas import (
    ChatRequest, ChatResponse, TypingStatus, ConversationSummary, 
    ChatSettings, CitationInfo, ErrorResponse
)
from app.dependencies import get_langgraph_agent
from app.services.langgraph_agent import LangGraphAgent
from app.services.citation_processor import get_citation_processor
from app.config import settings

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def enhanced_chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    agent: LangGraphAgent = Depends(get_langgraph_agent),
):
    """
    Enhanced chat endpoint with interactive features and citation linking
    
    Features:
    - Citation processing and linking
    - Suggested follow-up questions
    - Interactive UI elements
    - Quality metrics
    - Real-time processing updates
    """
    try:
        start_time = time.time()
        citation_processor = get_citation_processor()
        
        # Generate conversation ID and message ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        message_id = f"msg_{int(time.time() * 1000)}"
        
        # Process the chat message through LangGraph agent
        response_data = await agent.process_message(
            message=request.message,
            conversation_id=conversation_id,
            use_hybrid_search=request.use_hybrid_search,
        )
        
        # Extract basic response data
        raw_response = response_data["response"]
        sources = response_data.get("sources", [])
        entities = response_data.get("entities_mentioned", [])
        rag_quality = response_data.get("rag_quality", {})
        
        # Process citations and create interactive links
        processed_response, citations = citation_processor.process_response_citations(
            raw_response, sources
        )
        
        # Generate suggested follow-up questions
        suggested_questions = citation_processor.generate_suggested_questions(
            raw_response, entities, sources
        )
        
        # Create interactive UI elements
        interactive_elements = citation_processor.create_interactive_elements(
            raw_response, entities, rag_quality
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create enhanced response
        response = ChatResponse(
            response=processed_response,
            conversation_id=conversation_id,
            message_id=message_id,
            sources=sources,
            citations=citations,
            entities_mentioned=entities,
            rag_quality=rag_quality,
            processing_time=processing_time,
            suggested_questions=suggested_questions,
            response_metadata={
                "model_used": response_data.get("model_used"),
                "articles_used": response_data.get("articles_used", 0),
                "source_summary": response_data.get("source_summary", []),
                "response_style": request.response_style,
                "timestamp": time.time()
            },
            interactive_elements=interactive_elements
        )
        
        # Log metrics for debugging
        if settings.debug:
            print(f"Enhanced Chat Metrics:")
            print(f"  • Processing time: {processing_time:.2f}s")
            print(f"  • Citations: {len(citations)}")
            print(f"  • Quality score: {rag_quality.get('quality_score', 0):.2f}")
            print(f"  • Articles used: {response_data.get('articles_used', 0)}")
            print(f"  • Suggestions: {len(suggested_questions)}")
        
        # Background task to store conversation (optional)
        # background_tasks.add_task(store_conversation_message, conversation_id, request.message, response)
        
        return response
        
    except Exception as e:
        print(f"Enhanced chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/citations/{citation_id}/verify")
async def verify_citation(citation_id: str):
    """
    Verify a specific citation and return detailed information for cross-checking
    """
    try:
        citation_processor = get_citation_processor()
        
        # In production, retrieve citation from database
        # For now, return example verification data
        verification_data = {
            "citation_id": citation_id,
            "verification_status": "verified",
            "source_details": {
                "title": "Example Article Title",
                "publication": "TechNews",
                "published_date": "2024-01-15",
                "url": "https://example.com/article",
                "snippet": "This is a snippet from the original source...",
                "similarity_score": 0.87
            },
            "verification_methods": [
                {
                    "type": "source_check",
                    "label": "View Original Source",
                    "url": "https://example.com/article",
                    "available": True,
                    "status": "accessible"
                },
                {
                    "type": "similarity_check",
                    "label": "Relevance Score",
                    "score": 0.87,
                    "available": True,
                    "interpretation": "High relevance"
                }
            ],
            "trust_indicators": {
                "has_url": True,
                "has_date": True,
                "high_relevance": True,
                "known_publication": True,
                "trust_score": 0.92
            }
        }
        
        return verification_data
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify citation: {str(e)}"
        )


@router.post("/typing-status")
async def update_typing_status(status: TypingStatus):
    """
    Update typing status for real-time UI updates
    """
    try:
        # In production, broadcast to WebSocket connections
        return {
            "status": "updated",
            "conversation_id": status.conversation_id,
            "is_typing": status.is_typing,
            "stage": status.stage
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update typing status: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/summary", response_model=ConversationSummary)
async def get_conversation_summary(conversation_id: str):
    """
    Get an AI-generated summary of the conversation
    """
    try:
        citation_processor = get_citation_processor()
        
        # In production, retrieve messages from database and generate summary
        summary = ConversationSummary(
            conversation_id=conversation_id,
            title="AI Technology Discussion",
            message_count=5,
            last_updated=datetime.now(),
            topics_discussed=["AI Development", "Technology Trends", "Industry News"],
            key_insights=[
                "Recent breakthroughs in AI language understanding",
                "New developments in tech industry",
                "Emerging trends in automation"
            ],
            mood="informative"
        )
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate conversation summary: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/history")
async def get_conversation_history(
    conversation_id: str,
    limit: int = 50,
):
    """
    Get enhanced conversation history with metadata
    """
    try:
        # For now, return example history
        # In production, retrieve from database
        return {
            "conversation_id": conversation_id,
            "messages": [],
            "total_messages": 0,
            "conversation_metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "message_count": 0,
                "topics_discussed": [],
                "average_response_time": 0,
                "total_sources_used": 0
            },
            "message": "Enhanced conversation history - implementation pending"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve conversation history: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/follow-up")
async def generate_follow_up_questions(
    conversation_id: str,
    agent: LangGraphAgent = Depends(get_langgraph_agent)
):
    """
    Generate contextual follow-up questions based on conversation
    """
    try:
        citation_processor = get_citation_processor()
        
        # In production, analyze conversation history to generate better questions
        follow_up_questions = [
            "Can you elaborate on the sources mentioned?",
            "What are the latest developments in this area?",
            "How does this compare to previous findings?",
            "What are the potential implications?",
            "Are there any alternative perspectives?",
            "What should I know about the key players involved?"
        ]
        
        return {
            "conversation_id": conversation_id,
            "follow_up_questions": follow_up_questions[:4],  # Return top 4
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate follow-up questions: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    format: str = "json"  # json, markdown, pdf
):
    """
    Export conversation in various formats
    """
    try:
        if format == "json":
            export_data = {
                "conversation_id": conversation_id,
                "exported_at": datetime.now().isoformat(),
                "format": "json",
                "messages": [],  # Would include full conversation
                "metadata": {
                    "total_messages": 0,
                    "total_sources": 0,
                    "topics_discussed": [],
                    "export_version": "1.0"
                }
            }
            
            return JSONResponse(content=export_data)
        
        elif format == "markdown":
            # Return markdown formatted conversation
            markdown_content = f"# Conversation Export\n\n**Conversation ID:** {conversation_id}\n**Exported:** {datetime.now().isoformat()}\n\n## Messages\n\n*No messages available in demo*"
            
            return JSONResponse(
                content={"content": markdown_content, "format": "markdown"},
                headers={"Content-Type": "application/json"}
            )
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export conversation: {str(e)}"
        )


@router.post("/settings", response_model=ChatSettings)
async def update_chat_settings(settings: ChatSettings):
    """
    Update user chat settings and preferences
    """
    try:
        # In production, store in user preferences database
        return settings
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update settings: {str(e)}"
        )


@router.get("/settings", response_model=ChatSettings)
async def get_chat_settings():
    """
    Get current chat settings and preferences
    """
    try:
        # Return default settings for demo
        return ChatSettings()
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve settings: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation and its history
    """
    try:
        # In production, implement proper deletion with confirmation
        return {
            "message": f"Conversation {conversation_id} deleted successfully",
            "deleted_at": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete conversation: {str(e)}"
        )


@router.get("/conversations")
async def list_conversations(
    limit: int = 20,
    offset: int = 0,
):
    """
    List user's conversations with enhanced metadata
    """
    try:
        # Return example conversations for demo
        conversations = [
            {
                "conversation_id": f"conv_{i}",
                "title": f"Discussion {i+1}",
                "last_message": "Recent AI developments...",
                "last_updated": datetime.now().isoformat(),
                "message_count": 5 + i,
                "topics": ["AI", "Technology"],
                "mood": "informative",
                "has_sources": True
            }
            for i in range(min(3, limit))  # Return max 3 demo conversations
        ]
        
        return {
            "conversations": conversations,
            "total_count": len(conversations),
            "has_more": False,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total_pages": 1
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list conversations: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/feedback")
async def submit_conversation_feedback(
    conversation_id: str,
    feedback: Dict[str, Any]
):
    """
    Submit feedback for conversation quality improvement
    """
    try:
        return {
            "conversation_id": conversation_id,
            "feedback_received": True,
            "submitted_at": datetime.now().isoformat(),
            "message": "Thank you for your feedback!"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit feedback: {str(e)}"
        )
