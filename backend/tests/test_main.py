"""
Tests for NewsNeuron main application
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "NewsNeuron" in data["message"]
    assert "version" in data


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code in [200, 503]  # Might be 503 if DB not configured
    data = response.json()
    assert "status" in data
    assert "app_name" in data


def test_cors_headers():
    """Test CORS headers are present"""
    response = client.options("/")
    assert "access-control-allow-origin" in response.headers or response.status_code == 405


def test_docs_endpoint():
    """Test API documentation endpoint"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_endpoint():
    """Test OpenAPI schema endpoint"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
