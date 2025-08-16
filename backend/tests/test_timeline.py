"""
Tests for timeline functionality
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_generate_timeline():
    """Test timeline generation endpoint"""
    timeline_request = {
        "entity_name": "OpenAI",
        "limit": 20
    }
    
    response = client.post("/api/v1/timeline/", json=timeline_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "entity_name" in data
    assert "events" in data
    assert "total_events" in data
    assert "date_range" in data


def test_get_entity_timeline():
    """Test get entity timeline endpoint"""
    entity_name = "Tesla"
    response = client.get(f"/api/v1/timeline/{entity_name}", params={
        "limit": 15
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["entity_name"] == entity_name
    assert "events" in data


def test_timeline_with_date_range():
    """Test timeline generation with date range"""
    start_date = (datetime.now() - timedelta(days=30)).isoformat()
    end_date = datetime.now().isoformat()
    
    timeline_request = {
        "entity_name": "Elon Musk",
        "start_date": start_date,
        "end_date": end_date,
        "limit": 25
    }
    
    response = client.post("/api/v1/timeline/", json=timeline_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "date_range" in data


def test_timeline_summary():
    """Test timeline summary endpoint"""
    entity_name = "Microsoft"
    response = client.get(f"/api/v1/timeline/{entity_name}/summary", params={
        "days_back": 30
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "entity_name" in data
    assert "time_period" in data
    assert "summary" in data


def test_related_entities_timeline():
    """Test related entities timeline endpoint"""
    entity_name = "Google"
    response = client.get(f"/api/v1/timeline/{entity_name}/related", params={
        "max_depth": 2,
        "limit": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "entity_name" in data
    assert "related_entities" in data
    assert "max_depth" in data


def test_trending_events():
    """Test trending events endpoint"""
    response = client.get("/api/v1/timeline/events/trending", params={
        "days_back": 7,
        "limit": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "trending_events" in data
    assert "time_period_days" in data


def test_timeline_invalid_entity():
    """Test timeline with empty entity name"""
    timeline_request = {
        "entity_name": "",  # Empty entity name
        "limit": 10
    }
    
    response = client.post("/api/v1/timeline/", json=timeline_request)
    assert response.status_code == 422  # Validation error


def test_timeline_invalid_limit():
    """Test timeline with invalid limit"""
    timeline_request = {
        "entity_name": "Apple",
        "limit": 0  # Invalid limit
    }
    
    response = client.post("/api/v1/timeline/", json=timeline_request)
    assert response.status_code == 422  # Validation error


def test_timeline_high_limit():
    """Test timeline with limit above maximum"""
    timeline_request = {
        "entity_name": "Amazon",
        "limit": 150  # Above maximum
    }
    
    response = client.post("/api/v1/timeline/", json=timeline_request)
    assert response.status_code == 422  # Validation error


def test_timeline_summary_invalid_days():
    """Test timeline summary with invalid days_back"""
    entity_name = "Facebook"
    response = client.get(f"/api/v1/timeline/{entity_name}/summary", params={
        "days_back": 0  # Invalid days_back
    })
    
    assert response.status_code == 422  # Validation error
