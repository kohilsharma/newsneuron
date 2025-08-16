"""
Tests for chat functionality
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_chat_endpoint():
    """Test chat endpoint with valid request"""
    chat_request = {
        "message": "Tell me about recent AI developments",
        "use_hybrid_search": True
    }
    
    response = client.post("/api/v1/chat/", json=chat_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data
    assert "sources" in data
    assert "entities_mentioned" in data


def test_chat_endpoint_invalid_request():
    """Test chat endpoint with invalid request"""
    invalid_request = {
        "message": "",  # Empty message should fail validation
    }
    
    response = client.post("/api/v1/chat/", json=invalid_request)
    assert response.status_code == 422  # Validation error


def test_chat_endpoint_missing_message():
    """Test chat endpoint with missing message field"""
    invalid_request = {
        "use_hybrid_search": True
    }
    
    response = client.post("/api/v1/chat/", json=invalid_request)
    assert response.status_code == 422  # Validation error


def test_conversation_history():
    """Test conversation history endpoint"""
    conversation_id = "test-conversation-123"
    response = client.get(f"/api/v1/chat/conversations/{conversation_id}/history")
    
    # Should return 200 even if conversation doesn't exist (empty history)
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data


def test_list_conversations():
    """Test list conversations endpoint"""
    response = client.get("/api/v1/chat/conversations")
    assert response.status_code == 200
    
    data = response.json()
    assert "conversations" in data
    assert "total_count" in data


def test_delete_conversation():
    """Test delete conversation endpoint"""
    conversation_id = "test-conversation-123"
    response = client.delete(f"/api/v1/chat/conversations/{conversation_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
