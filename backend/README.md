# NewsNeuron Backend

A high-performance FastAPI backend providing AI-powered news analysis with hybrid vector-graph intelligence.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI 0.116+](https://img.shields.io/badge/FastAPI-0.116+-red.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.6+-purple.svg)](https://langgraph.com/)

## 🚀 Features

- **FastAPI Framework**: High-performance async API with automatic OpenAPI documentation
- **Hybrid AI Intelligence**: Combines vector search with knowledge graph traversal
- **Multi-Agent Workflows**: LangGraph orchestration for complex reasoning tasks
- **Dual Database Architecture**: PostgreSQL + pgvector for semantic search, Neo4j for graph relationships
- **Advanced NLP**: spaCy integration for entity extraction and text processing
- **Comprehensive Testing**: pytest with async support and comprehensive test coverage
- **Production Ready**: Docker support, proper logging, error handling, and monitoring

## 🏗️ Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and settings
│   ├── dependencies.py      # Dependency injection
│   ├── schemas.py           # Pydantic models and schemas
│   ├── routers/            # API endpoint routers
│   │   ├── chat.py         # AI chat endpoints
│   │   ├── flashcards.py   # Flashcard generation endpoints
│   │   ├── search.py       # Search and discovery endpoints
│   │   └── timeline.py     # Timeline analysis endpoints
│   ├── services/           # Business logic layer
│   │   ├── ai/             # AI and ML services
│   │   ├── chat_service.py # Chat conversation management
│   │   ├── search_service.py # Hybrid search implementation
│   │   └── timeline_service.py # Timeline generation
│   ├── database/           # Database clients and models
│   │   ├── supabase_client.py # Supabase connection
│   │   ├── neo4j_client.py    # Neo4j connection
│   │   └── models/            # Database models
│   └── utils/              # Utility functions
├── data-processing/        # Data ingestion pipeline
├── database/              # Database schemas and migrations
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
├── requirements.in        # Dependency specifications
└── Dockerfile            # Container configuration
```

## 🛠️ Technology Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Web Framework** | FastAPI | 0.116+ | High-performance async API |
| **AI Orchestration** | LangGraph | 0.6+ | Multi-agent workflow management |
| **Language Models** | LangChain + OpenAI | Latest | RAG and conversation chains |
| **Vector Database** | Supabase + pgvector | Latest | Semantic search and embeddings |
| **Graph Database** | Neo4j | 5.28+ | Entity relationships and graph queries |
| **NLP Processing** | spaCy | 3.7+ | Named entity recognition and text processing |
| **Data Processing** | pandas + numpy | Latest | Data manipulation and analysis |
| **Testing** | pytest + pytest-asyncio | Latest | Async testing framework |
| **Code Quality** | Black + flake8 | Latest | Code formatting and linting |
| **Validation** | Pydantic | 2.11+ | Data validation and serialization |
| **HTTP Client** | httpx | Latest | Async HTTP client for external APIs |

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **pip** or **poetry**
- **Virtual environment** (recommended)

### Installation

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Set up environment variables**:
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # Database Configuration
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_password
   
   # AI Services
   OPENAI_API_KEY=your_openai_api_key
   OPENROUTER_API_KEY=your_openrouter_api_key
   
   # Application Settings
   DEBUG=True
   SECRET_KEY=your_secret_key_here
   ```

6. **Start the development server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📜 Available Scripts

| Command | Description |
|---------|-------------|
| `uvicorn app.main:app --reload` | Start development server with auto-reload |
| `pytest` | Run test suite |
| `pytest --cov=app` | Run tests with coverage report |
| `black .` | Format code with Black |
| `flake8 .` | Lint code with flake8 |
| `pip-compile requirements.in` | Update requirements.txt |

## 🔌 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API status and information |
| `GET` | `/health` | Health check with database status |
| `GET` | `/docs` | Interactive API documentation |

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/chat/` | Send message to AI assistant |
| `GET` | `/api/v1/chat/conversations` | List user conversations |
| `GET` | `/api/v1/chat/conversations/{id}/history` | Get conversation history |
| `DELETE` | `/api/v1/chat/conversations/{id}` | Delete conversation |

### Search Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/search/` | Hybrid vector-graph search |
| `GET` | `/api/v1/search/` | Alternative search endpoint |
| `GET` | `/api/v1/search/entities` | Search entities in knowledge graph |
| `GET` | `/api/v1/search/similar/{article_id}` | Find similar articles |

### Flashcards Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/flashcards/` | Generate AI flashcards |
| `GET` | `/api/v1/flashcards/` | Get recent flashcards |
| `GET` | `/api/v1/flashcards/{id}` | Get specific flashcard |
| `GET` | `/api/v1/flashcards/topics/trending` | Get trending topics |

### Timeline Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/timeline/` | Generate entity timeline |
| `GET` | `/api/v1/timeline/{entity}` | Get entity timeline |
| `GET` | `/api/v1/timeline/{entity}/summary` | Get timeline summary |
| `GET` | `/api/v1/timeline/{entity}/related` | Get related entities |

## 🧠 AI Services

### LangGraph Workflows

The backend uses **LangGraph** for orchestrating complex AI workflows:

```python
# Example: Multi-agent search workflow
from langgraph import Graph
from app.services.ai.agents import SearchAgent, AnalysisAgent, SummaryAgent

def create_search_workflow():
    workflow = Graph()
    
    # Add agents
    workflow.add_node("search", SearchAgent())
    workflow.add_node("analysis", AnalysisAgent())
    workflow.add_node("summary", SummaryAgent())
    
    # Define flow
    workflow.add_edge("search", "analysis")
    workflow.add_edge("analysis", "summary")
    
    return workflow.compile()
```

### Vector Search

Semantic search using **OpenAI embeddings** and **pgvector**:

```python
async def semantic_search(query: str, limit: int = 10):
    # Generate query embedding
    embedding = await openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=query
    )
    
    # Search in Supabase
    results = await supabase.rpc(
        'semantic_search',
        {
            'query_embedding': embedding.data[0].embedding,
            'similarity_threshold': 0.7,
            'match_count': limit
        }
    )
    
    return results.data
```

### Knowledge Graph Queries

Graph traversal using **Neo4j** for entity relationships:

```python
async def get_entity_relationships(entity_name: str):
    query = """
    MATCH (e:Entity {name: $entity_name})-[r]->(related:Entity)
    RETURN e, r, related
    ORDER BY r.strength DESC
    LIMIT 20
    """
    
    async with driver.session() as session:
        result = await session.run(query, entity_name=entity_name)
        return [record.data() for record in result]
```

## 🗄️ Database Layer

### Supabase (PostgreSQL + pgvector)

Used for:
- **Article storage**: Full-text content and metadata
- **Vector embeddings**: Semantic search capabilities
- **User data**: Conversations and preferences

```python
# Example: Article insertion with embedding
async def insert_article(article_data: dict, embedding: list):
    result = await supabase.table('articles').insert({
        'title': article_data['title'],
        'content': article_data['content'],
        'embedding': embedding,
        'published_date': article_data['published_date']
    }).execute()
    
    return result.data[0]
```

### Neo4j Graph Database

Used for:
- **Entity relationships**: People, organizations, locations
- **Event timelines**: Temporal relationships
- **Semantic connections**: Concept relationships

```python
# Example: Entity relationship creation
async def create_entity_relationship(entity1: str, entity2: str, relation_type: str):
    query = """
    MERGE (e1:Entity {name: $entity1})
    MERGE (e2:Entity {name: $entity2})
    MERGE (e1)-[r:RELATES_TO {type: $relation_type}]->(e2)
    SET r.strength = coalesce(r.strength, 0) + 1
    """
    
    async with driver.session() as session:
        await session.run(query, 
                         entity1=entity1, 
                         entity2=entity2, 
                         relation_type=relation_type)
```

## 🧪 Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Pytest configuration and fixtures
├── test_main.py             # Application-level tests
├── routers/                 # API endpoint tests
│   ├── test_chat.py
│   ├── test_search.py
│   └── test_flashcards.py
├── services/                # Business logic tests
│   ├── test_chat_service.py
│   └── test_search_service.py
└── database/                # Database integration tests
    ├── test_supabase.py
    └── test_neo4j.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/routers/test_chat.py

# Run with verbose output
pytest -v

# Run async tests
pytest -k "test_async"
```

### Example Test

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_chat_endpoint():
    response = client.post(
        "/api/v1/chat/",
        json={
            "message": "Tell me about AI",
            "use_hybrid_search": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data
```

## 📊 Data Processing Pipeline

### Article Ingestion

```python
# data-processing/ingest.py
async def process_articles(articles: List[Dict]):
    for article in articles:
        # 1. Extract entities using spaCy
        entities = extract_entities(article['content'])
        
        # 2. Generate embeddings
        embedding = await generate_embedding(article['content'])
        
        # 3. Store in Supabase
        article_id = await store_article(article, embedding)
        
        # 4. Create graph relationships
        await create_graph_entities(entities, article_id)
        
        # 5. Update search index
        await update_search_index(article_id)
```

### Entity Extraction

```python
import spacy

nlp = spacy.load("en_core_web_sm")

def extract_entities(text: str) -> List[Dict]:
    doc = nlp(text)
    entities = []
    
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT"]:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": ent._.confidence if hasattr(ent._, 'confidence') else 1.0
            })
    
    return entities
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SUPABASE_URL` | Supabase project URL | Yes | - |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | Yes | - |
| `NEO4J_URI` | Neo4j connection URI | Yes | `bolt://localhost:7687` |
| `NEO4J_USERNAME` | Neo4j username | Yes | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | Yes | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `OPENROUTER_API_KEY` | OpenRouter API key | No | - |
| `DEBUG` | Enable debug mode | No | `False` |
| `SECRET_KEY` | JWT secret key | Yes | - |
| `CORS_ORIGINS` | Allowed CORS origins | No | `["*"]` |

### Settings Management

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "NewsNeuron API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    supabase_url: str
    supabase_anon_key: str
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str
    
    # AI Services
    openai_api_key: str
    openrouter_api_key: str = ""
    
    # Security
    secret_key: str
    cors_origins: List[str] = ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 🚀 Deployment

### Docker Support

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application
COPY app/ ./app/
COPY data-processing/ ./data-processing/
COPY database/ ./database/

# Expose port
EXPOSE 8000

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. **Environment Variables**: Use secure secret management
2. **Database Connections**: Connection pooling and SSL
3. **Logging**: Structured logging with proper levels
4. **Monitoring**: Health checks and metrics
5. **Security**: Rate limiting and input validation

## 🔍 Monitoring & Logging

### Logging Configuration

```python
import logging
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "databases": {
            "supabase": await check_supabase_connection(),
            "neo4j": await check_neo4j_connection()
        }
    }
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   ```bash
   # Check environment variables
   echo $SUPABASE_URL
   echo $NEO4J_URI
   
   # Test database connections
   python -c "from app.database.supabase_client import get_supabase_client; print('Supabase OK')"
   ```

2. **spaCy Model Missing**:
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Import Errors**:
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

4. **API Key Issues**:
   ```bash
   # Verify API keys are set
   python -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY')))"
   ```

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example Usage

```python
import httpx

# Chat with AI
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/chat/",
        json={
            "message": "What are the latest AI developments?",
            "use_hybrid_search": True
        }
    )
    print(response.json())

# Search articles
response = await client.post(
    "http://localhost:8000/api/v1/search/",
    json={
        "query": "artificial intelligence",
        "search_type": "hybrid",
        "limit": 5
    }
)
```

## 🤝 Contributing

1. **Code Style**: Follow PEP 8 and use Black for formatting
2. **Type Hints**: Use type hints for all function signatures
3. **Documentation**: Document all public functions and classes
4. **Testing**: Write tests for new features
5. **Async First**: Use async/await for I/O operations

For detailed guidelines, see [CONTRIBUTING.md](../CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🔗 Related Documentation

- [Frontend Documentation](../frontend/README.md)
- [API Documentation](../docs/API.md)
- [Setup Guide](../docs/SETUP.md)
- [Database Schema](../docs/DATABASE.md)
