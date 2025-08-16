"""
Chat API endpoints for NewsNeuron
Handles AI chatbot interactions with hybrid retrieval
"""
import uuid
import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.schemas import ChatRequest, ChatResponse, ErrorResponse
from app.dependencies import get_langgraph_agent, get_current_user
from app.services.langgraph_agent import LangGraphAgent

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    agent: LangGraphAgent = Depends(get_langgraph_agent),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Main chat endpoint for AI assistant interaction
    
    Uses LangGraph agent with hybrid vector-graph retrieval for context-aware responses
    """
    try:
        start_time = time.time()
        
        # Generate conversation ID if not provided
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Process the chat message through LangGraph agent
        response_data = await agent.process_message(
            message=request.message,
            conversation_id=conversation_id,
            use_hybrid_search=request.use_hybrid_search,
            user_id=current_user.get("id")
        )
        
        # Prepare response
        response = ChatResponse(
            response=response_data["response"],
            conversation_id=conversation_id,
            sources=response_data.get("sources", []),
            entities_mentioned=response_data.get("entities_mentioned", [])
        )
        
        # Log the interaction time
        processing_time = time.time() - start_time
        print(f"Chat processing time: {processing_time:.2f}s")
        
        return response
        
    except Exception as e:
        print(f"Chat endpoint error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/history")
async def get_conversation_history(
    conversation_id: str,
    limit: int = 50,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get conversation history for a specific conversation
    TODO: Implement conversation storage in database
    """
    try:
        # For now, return empty history
        # This will be implemented when conversation storage is added
        return {
            "conversation_id": conversation_id,
            "messages": [],
            "total_messages": 0,
            "message": "Conversation history not implemented yet"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve conversation history: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a conversation and its history
    TODO: Implement conversation deletion when storage is added
    """
    try:
        # For now, return success
        # This will be implemented when conversation storage is added
        return {
            "message": f"Conversation {conversation_id} deleted successfully",
            "note": "Conversation deletion not implemented yet"
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
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List user's conversations
    TODO: Implement when conversation storage is added
    """
    try:
        # For now, return empty list
        return {
            "conversations": [],
            "total_count": 0,
            "message": "Conversation listing not implemented yet"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list conversations: {str(e)}"
        )
