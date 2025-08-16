"""
Tests for flashcard functionality
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_generate_flashcards():
    """Test flashcard generation endpoint"""
    flashcard_request = {
        "topics": ["technology", "AI"],
        "limit": 5
    }
    
    response = client.post("/api/v1/flashcards/", json=flashcard_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "flashcards" in data
    assert "total_count" in data
    assert isinstance(data["flashcards"], list)


def test_get_recent_flashcards():
    """Test get recent flashcards endpoint"""
    response = client.get("/api/v1/flashcards/", params={
        "limit": 10,
        "days_back": 7
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "flashcards" in data
    assert "total_count" in data


def test_get_recent_flashcards_with_topics():
    """Test get recent flashcards with topic filter"""
    response = client.get("/api/v1/flashcards/", params={
        "limit": 5,
        "topics": ["technology", "politics"],
        "days_back": 30
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "flashcards" in data


def test_get_flashcard_details():
    """Test get specific flashcard details"""
    flashcard_id = "test-flashcard-123"
    response = client.get(f"/api/v1/flashcards/{flashcard_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert "flashcard" in data


def test_trending_topics():
    """Test trending topics endpoint"""
    response = client.get("/api/v1/flashcards/topics/trending", params={
        "limit": 10,
        "days_back": 7
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "trending_topics" in data
    assert "time_period_days" in data


def test_flashcard_generation_invalid_limit():
    """Test flashcard generation with invalid limit"""
    flashcard_request = {
        "limit": 0  # Invalid limit
    }
    
    response = client.post("/api/v1/flashcards/", json=flashcard_request)
    assert response.status_code == 422  # Validation error


def test_flashcard_generation_high_limit():
    """Test flashcard generation with high limit"""
    flashcard_request = {
        "limit": 25  # Above maximum
    }
    
    response = client.post("/api/v1/flashcards/", json=flashcard_request)
    assert response.status_code == 422  # Validation error


def test_flashcard_generation_with_date_range():
    """Test flashcard generation with date range"""
    flashcard_request = {
        "date_range": {
            "start_date": "2024-01-01T00:00:00Z",
            "end_date": "2024-01-31T23:59:59Z"
        },
        "limit": 5
    }
    
    response = client.post("/api/v1/flashcards/", json=flashcard_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "flashcards" in data
