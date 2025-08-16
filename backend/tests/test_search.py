"""
Tests for search functionality
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_search_endpoint_post():
    """Test search endpoint with POST request"""
    search_request = {
        "query": "artificial intelligence",
        "search_type": "hybrid",
        "limit": 5,
        "include_entities": True
    }
    
    response = client.post("/api/v1/search/", json=search_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "results" in data
    assert "total_results" in data
    assert "query_entities" in data
    assert "search_time_ms" in data


def test_search_endpoint_get():
    """Test search endpoint with GET request"""
    response = client.get("/api/v1/search/", params={
        "q": "climate change",
        "search_type": "vector",
        "limit": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


def test_search_suggestions():
    """Test search suggestions endpoint"""
    response = client.get("/api/v1/search/suggestions", params={
        "query": "tech",
        "limit": 5
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert "query" in data


def test_search_entities():
    """Test entity search endpoint"""
    response = client.get("/api/v1/search/entities", params={
        "query": "OpenAI",
        "limit": 10
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert "total_count" in data


def test_search_entities_with_type_filter():
    """Test entity search with type filter"""
    response = client.get("/api/v1/search/entities", params={
        "query": "tech",
        "entity_type": "ORGANIZATION",
        "limit": 5
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert "filters" in data


def test_find_similar_articles():
    """Test find similar articles endpoint"""
    article_id = 1
    response = client.get(f"/api/v1/search/similar/{article_id}", params={
        "limit": 5,
        "similarity_threshold": 0.7
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "article_id" in data
    assert "similar_articles" in data
    assert "total_count" in data


def test_search_invalid_query():
    """Test search with invalid query"""
    search_request = {
        "query": "",  # Empty query should fail
        "search_type": "hybrid"
    }
    
    response = client.post("/api/v1/search/", json=search_request)
    assert response.status_code == 422  # Validation error


def test_search_invalid_type():
    """Test search with invalid search type"""
    search_request = {
        "query": "test query",
        "search_type": "invalid_type"
    }
    
    response = client.post("/api/v1/search/", json=search_request)
    # Should either accept it or return validation error
    assert response.status_code in [200, 422]
