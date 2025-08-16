# NewsNeuron API Documentation

This document provides detailed information about the NewsNeuron API endpoints, request/response formats, and usage examples.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.vercel.app`

## Authentication

Currently, the API is open for development. Authentication will be implemented in future versions.

## API Endpoints

### Health Check

#### GET `/`
Get basic API information.

**Response:**
```json
{
  "message": "Welcome to NewsNeuron API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

#### GET `/health`
Check API and database health status.

**Response:**
```json
{
  "status": "healthy",
  "app_name": "NewsNeuron",
  "version": "1.0.0",
  "databases": {
    "supabase": "connected",
    "neo4j": "connected"
  }
}
```

---

## Chat Endpoints

### POST `/api/v1/chat/`
Send a message to the AI assistant.

**Request Body:**
```json
{
  "message": "Tell me about recent AI developments",
  "conversation_id": "optional-conversation-id",
  "use_hybrid_search": true
}
```

**Response:**
```json
{
  "response": "Recent AI developments include...",
  "conversation_id": "uuid-string",
  "sources": [
    {
      "title": "Article Title",
      "url": "https://example.com/article",
      "source": "TechNews",
      "published_date": "2024-01-15T10:00:00Z"
    }
  ],
  "entities_mentioned": ["OpenAI", "GPT-4", "Machine Learning"]
}
```

### GET `/api/v1/chat/conversations`
List user conversations.

**Query Parameters:**
- `limit` (optional): Maximum number of conversations (default: 20)
- `offset` (optional): Number of conversations to skip (default: 0)

**Response:**
```json
{
  "conversations": [
    {
      "id": "uuid-string",
      "title": "AI Discussion",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T11:30:00Z"
    }
  ],
  "total_count": 5
}
```

### GET `/api/v1/chat/conversations/{conversation_id}/history`
Get conversation message history.

**Path Parameters:**
- `conversation_id`: Conversation UUID

**Query Parameters:**
- `limit` (optional): Maximum number of messages (default: 50)

**Response:**
```json
{
  "conversation_id": "uuid-string",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-15T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "Hi! How can I help you?",
      "timestamp": "2024-01-15T10:00:05Z"
    }
  ],
  "total_messages": 10
}
```

---

## Search Endpoints

### POST `/api/v1/search/`
Search articles using hybrid vector-graph approach.

**Request Body:**
```json
{
  "query": "artificial intelligence trends",
  "search_type": "hybrid",
  "limit": 10,
  "include_entities": true
}
```

**Response:**
```json
{
  "results": [
    {
      "id": 123,
      "title": "AI Breakthrough in Language Models",
      "content": "Recent developments in AI...",
      "url": "https://example.com/article",
      "published_date": "2024-01-15T10:00:00Z",
      "source": "TechNews",
      "similarity_score": 0.89,
      "entities": [
        {"name": "OpenAI", "type": "ORGANIZATION"}
      ]
    }
  ],
  "total_results": 25,
  "query_entities": ["artificial intelligence"],
  "search_time_ms": 150.5
}
```

### GET `/api/v1/search/`
Alternative GET endpoint for search.

**Query Parameters:**
- `q`: Search query (required)
- `search_type`: "vector", "graph", or "hybrid" (default: "hybrid")
- `limit`: Maximum results (default: 10, max: 50)
- `include_entities`: Include entity information (default: true)

### GET `/api/v1/search/entities`
Search for entities in the knowledge graph.

**Query Parameters:**
- `query`: Entity search query (required)
- `entity_type`: Filter by type (optional): "PERSON", "ORGANIZATION", "LOCATION", "EVENT"
- `limit`: Maximum results (default: 20, max: 50)

**Response:**
```json
{
  "entities": [
    {
      "name": "OpenAI",
      "type": "ORGANIZATION",
      "mention_count": 45
    }
  ],
  "total_count": 15,
  "search_time_ms": 25.3
}
```

### GET `/api/v1/search/similar/{article_id}`
Find articles similar to a specific article.

**Path Parameters:**
- `article_id`: Article ID

**Query Parameters:**
- `limit`: Maximum similar articles (default: 10, max: 20)
- `similarity_threshold`: Minimum similarity score (default: 0.7)

---

## Flashcard Endpoints

### POST `/api/v1/flashcards/`
Generate AI-summarized flashcards.

**Request Body:**
```json
{
  "topics": ["technology", "AI"],
  "date_range": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z"
  },
  "limit": 10
}
```

**Response:**
```json
{
  "flashcards": [
    {
      "id": "uuid-string",
      "title": "AI Breakthrough in Language Models",
      "summary": "Recent developments show significant progress...",
      "key_points": [
        "GPT-4 shows improved reasoning",
        "Multimodal capabilities expanded",
        "Efficiency improvements noted"
      ],
      "entities": [
        {"name": "OpenAI", "type": "ORGANIZATION"}
      ],
      "source_articles": [
        {
          "id": 123,
          "title": "Article Title",
          "url": "https://example.com"
        }
      ],
      "created_at": "2024-01-15T10:00:00Z",
      "category": "Technology"
    }
  ],
  "total_count": 8
}
```

### GET `/api/v1/flashcards/`
Get recent flashcards.

**Query Parameters:**
- `limit`: Number of flashcards (default: 10, max: 20)
- `topics`: Filter by topics (optional, array)
- `days_back`: How many days to look back (default: 7, max: 30)

### GET `/api/v1/flashcards/topics/trending`
Get trending topics for flashcard generation.

**Query Parameters:**
- `limit`: Number of topics (default: 10, max: 20)
- `days_back`: Time period for analysis (default: 7, max: 30)

**Response:**
```json
{
  "trending_topics": [
    {
      "topic": "Artificial Intelligence",
      "mention_count": 45,
      "trend_score": 0.85
    }
  ],
  "time_period_days": 7
}
```

---

## Timeline Endpoints

### POST `/api/v1/timeline/`
Generate timeline for a specific entity.

**Request Body:**
```json
{
  "entity_name": "OpenAI",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-31T23:59:59Z",
  "limit": 50
}
```

**Response:**
```json
{
  "entity_name": "OpenAI",
  "events": [
    {
      "id": 123,
      "title": "OpenAI Releases GPT-4",
      "date": "2024-01-15T10:00:00Z",
      "description": "OpenAI announced the release of GPT-4...",
      "article_url": "https://example.com/article",
      "source": "TechNews",
      "entity_role": "mentioned",
      "related_entities": ["GPT-4", "AI"]
    }
  ],
  "total_events": 25,
  "date_range": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z"
  }
}
```

### GET `/api/v1/timeline/{entity_name}`
Alternative GET endpoint for entity timeline.

**Path Parameters:**
- `entity_name`: Name of the entity

**Query Parameters:**
- `start_date`: Timeline start date (optional)
- `end_date`: Timeline end date (optional)
- `limit`: Maximum events (default: 50, max: 100)

### GET `/api/v1/timeline/{entity_name}/summary`
Get timeline summary statistics.

**Response:**
```json
{
  "entity_name": "OpenAI",
  "time_period": {
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-31T23:59:59Z",
    "days": 30
  },
  "summary": {
    "total_events": 15,
    "average_events_per_day": 0.5,
    "most_active_period": {
      "week_start": "2024-01-15",
      "event_count": 5
    },
    "activity_trend": "increasing"
  }
}
```

---

## Error Handling

All endpoints return errors in a consistent format:

```json
{
  "success": false,
  "message": "Error description",
  "error_code": "VALIDATION_ERROR",
  "details": {
    "field": "Additional error details"
  }
}
```

### HTTP Status Codes

- `200`: Success
- `400`: Bad Request (validation error)
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Unprocessable Entity (validation error)
- `500`: Internal Server Error

---

## Rate Limiting

- **API endpoints**: 10 requests per second per IP
- **Search endpoints**: 5 requests per second per IP
- **Heavy operations**: 2 requests per second per IP

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Requests allowed per time window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

---

## Examples

### Python Example

```python
import requests

# Search for articles
response = requests.post('http://localhost:8000/api/v1/search/', json={
    'query': 'artificial intelligence',
    'search_type': 'hybrid',
    'limit': 5
})

articles = response.json()['results']
print(f"Found {len(articles)} articles")

# Chat with AI
chat_response = requests.post('http://localhost:8000/api/v1/chat/', json={
    'message': 'What are the latest AI developments?',
    'use_hybrid_search': True
})

answer = chat_response.json()['response']
print(f"AI Response: {answer}")
```

### JavaScript Example

```javascript
// Search for articles
const searchResponse = await fetch('http://localhost:8000/api/v1/search/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'climate change',
    search_type: 'hybrid',
    limit: 5
  })
});

const searchData = await searchResponse.json();
console.log('Articles found:', searchData.results.length);

// Generate flashcards
const flashcardResponse = await fetch('http://localhost:8000/api/v1/flashcards/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    topics: ['technology'],
    limit: 5
  })
});

const flashcards = await flashcardResponse.json();
console.log('Flashcards generated:', flashcards.flashcards.length);
```

---

## Interactive Documentation

For interactive API documentation with the ability to test endpoints:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide comprehensive documentation with request/response examples and the ability to test API calls directly from the browser.
