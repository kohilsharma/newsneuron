# Copilot Instructions for NewsNeuron

## Repository Overview

NewsNeuron is an AI-powered news analysis system that combines Retrieval-Augmented Generation (RAG) with Knowledge Graph technology. The system processes news like interconnected neurons, understanding both content and relationships between entities.

**Technology Stack:**
- **Frontend**: Vue.js 3.3+ with Composition API, Tailwind CSS 3.4+, Vite 7.1+ build tool
- **Backend**: FastAPI 0.116+ with Python 3.10+, LangGraph 0.6+ for AI workflows
- **AI**: LangChain + OpenRouter for LLMs, local sentence-transformers for embeddings (free)
- **Databases**: Supabase (PostgreSQL + pgvector) for vectors, Neo4j 5.28+ for knowledge graphs
- **Testing**: Vitest for frontend, pytest for backend
- **Code Quality**: ESLint 9 flat config + Prettier for frontend, Black + flake8 for backend
- **Deployment**: Vercel with Docker support

**Repository Size**: ~50 files, monorepo structure with separate frontend/backend directories.

## Critical Build Instructions

### Backend Setup (Python 3.10+)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
```

**IMPORTANT**: The current `requirements.txt` has dependency conflicts with Python 3.12+. For basic development:
```bash
# Install core dependencies first
pip install fastapi uvicorn pytest black flake8 pydantic python-dotenv

# For full functionality, manually install key packages:
pip install langchain langgraph supabase neo4j spacy sentence-transformers
python -m spacy download en_core_web_md
```

**Environment Setup:**
```bash
cp env.example .env
# Edit .env with your database credentials - see env.example for all required variables
```

**Run Development Server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# API docs available at: http://localhost:8000/docs
```

**Run Tests:**
```bash
pytest  # All tests
pytest tests/test_main.py  # Specific file
pytest --cov=app  # With coverage
```

**Linting/Formatting:**
```bash
black .  # Format code
flake8 .  # Lint code
```

### Frontend Setup (Node.js 18+)
```bash
cd frontend
npm install  # Takes ~21s, may show deprecation warnings (safe to ignore)
```

**Environment Setup:**
```bash
cp env.example .env
# Edit VITE_API_BASE_URL=http://localhost:8000
```

**Run Development Server:**
```bash
npm run dev  # Starts on http://localhost:5173
```

**Build for Production:**
```bash
npm run build  # Creates dist/ directory (~4s build time)
```

**IMPORTANT ESLint Issue:** The current ESLint config has a flat config format issue. Linting will fail with:
```
A config object has a "plugins" key defined as an array of strings.
Flat config requires "plugins" to be an object
```

**Workaround**: The build process works fine. For linting fixes, check the ESLint migration guide.

**Run Tests:**
```bash
npm run test  # Vitest (currently no test files exist)
npm run test:ui  # Vitest UI dashboard
```

**Other Commands:**
```bash
npm run preview  # Preview production build (runs on http://localhost:4173)
npm run format  # Format with Prettier
```

## Project Layout and Architecture

### Repository Structure
```
newsneuron/
├── frontend/              # Vue.js application
│   ├── src/
│   │   ├── components/    # Reusable Vue components
│   │   ├── views/         # Page-level components
│   │   ├── stores/        # Pinia state management
│   │   ├── services/      # API clients
│   │   ├── router/        # Vue Router config
│   │   └── main.js        # Application entry point
│   ├── eslint.config.js   # ESLint 9 flat config (has known issue)
│   ├── vite.config.js     # Vite build configuration
│   ├── tailwind.config.js # Tailwind CSS config
│   └── package.json       # Dependencies and scripts
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── main.py        # FastAPI app entry point
│   │   ├── config.py      # Application settings
│   │   ├── routers/       # API endpoint definitions
│   │   ├── services/      # Business logic (AI, RAG, etc.)
│   │   ├── database/      # DB clients (Supabase, Neo4j)
│   │   └── schemas.py     # Pydantic models
│   ├── tests/             # Backend test suite
│   ├── data-processing/   # Data ingestion pipeline
│   ├── requirements.txt   # Python dependencies (has conflicts)
│   └── env.example        # Environment variables template
├── docker-compose.yml     # Local development with databases
├── vercel.json           # Vercel deployment config
└── nginx.conf            # Production reverse proxy
```

### Key Configuration Files
- **Backend Config**: `backend/app/config.py` - Application settings using Pydantic
- **Frontend Config**: `frontend/vite.config.js` - Build configuration
- **ESLint**: `frontend/eslint.config.js` - Modern flat config format (ESLint 9)
- **Tailwind**: `frontend/tailwind.config.js` - CSS framework configuration
- **Docker**: `docker-compose.yml` - Local development with PostgreSQL, Neo4j, Redis

### Main API Endpoints
- `POST /api/v1/chat` - AI chatbot interaction with RAG
- `GET /api/v1/flashcards` - News flashcard summaries
- `GET /api/v1/search` - Semantic search with hybrid retrieval
- `GET /api/v1/timeline/{entity}` - Entity timeline visualization
- `GET /health` - Fast health check
- `GET /health/detailed` - Comprehensive health check with database tests

### Database Requirements
- **Supabase**: PostgreSQL with pgvector extension for semantic search
- **Neo4j**: Knowledge graph for entity relationships and traversal
- **Redis**: Optional caching layer (configured in docker-compose.yml)

### AI Architecture
- **RAG Pipeline**: Hybrid vector + graph retrieval using LangGraph workflows
- **Embeddings**: Local sentence-transformers (no API costs)
- **LLMs**: OpenRouter integration (configurable)
- **NLP**: spaCy for entity extraction (`en_core_web_md` model required)

## Validation and CI/CD

### No GitHub Actions
This repository does not have `.github/workflows/` directory or automated CI/CD pipelines.

### Manual Validation Steps
1. **Backend Validation:**
   ```bash
   cd backend && source venv/bin/activate
   pytest  # Run all tests
   black . && flake8 .  # Code quality
   uvicorn app.main:app --reload  # Start server
   curl http://localhost:8000/health  # Test endpoint
   ```

2. **Frontend Validation:**
   ```bash
   cd frontend
   npm run build  # Ensure build succeeds
   npm run preview  # Test production build
   # Note: npm run lint currently fails due to ESLint config issue
   ```

3. **Full Stack Integration:**
   ```bash
   # Terminal 1: Start backend
   cd backend && source venv/bin/activate && uvicorn app.main:app --reload
   
   # Terminal 2: Start frontend  
   cd frontend && npm run dev
   
   # Visit http://localhost:5173 and test API integration
   ```

### Docker Development
```bash
# Start all services (PostgreSQL, Neo4j, Redis, backend, frontend)
docker-compose up

# Production build with Nginx
docker-compose --profile production up
```

### Known Issues and Workarounds

1. **Backend Dependencies**: `requirements.txt` has conflicts with Python 3.12+
   - **Workaround**: Install core packages manually as shown above
   - **Issue**: `backports-asyncio-runner==1.2.0` not compatible with Python 3.12+

2. **ESLint Configuration**: Flat config format issue
   - **Issue**: `eslint . --fix` fails with plugins array error
   - **Workaround**: Build process works fine, skip linting temporarily
   - **Fix**: Update to proper ESLint 9 flat config format

3. **spaCy Model**: Required for NLP functionality
   - **Command**: `python -m spacy download en_core_web_md`
   - **Must run**: After installing spacy, before running backend

4. **Database Dependencies**: Optional but required for full functionality
   - **Supabase**: Configure URL and keys in `.env`
   - **Neo4j**: Set up connection credentials
   - **Fallback**: Backend starts without databases but with limited functionality

### Performance Considerations
- **Frontend Build**: ~4 seconds
- **Backend Startup**: Fast startup mode, heavy services initialize in background
- **npm install**: ~21 seconds with deprecation warnings (safe to ignore)
- **Dependencies**: Large AI/ML packages, consider using Docker for consistency
- **File Count**: ~50 source files, manageable repository size
- **Python Virtual Env**: Always required for backend development

### Deployment
- **Platform**: Vercel (configured in `vercel.json`)
- **Backend**: Python 3.9 runtime on Vercel
- **Frontend**: Static build deployment
- **Environment**: Set production environment variables in Vercel dashboard

### Typical Development Workflow
1. **Setup**: Follow backend/frontend setup instructions above
2. **Development**: Run both servers in separate terminals
3. **Testing**: Use `npm run build` (frontend) and `pytest` (backend) to validate
4. **Code Quality**: Apply `black .` and `npm run format` before commits
5. **Issues**: Check Known Issues section before troubleshooting

### Contributors and Commit Style
- **Team**: HARI (Backend), VARADA (Frontend), SANJAI (AI), ARYA (Data), KOHIL (DevOps)
- **Commits**: Follow Conventional Commits format (feat:, fix:, docs:, etc.)
- **Branches**: Use feature/, fix/, docs/ prefixes for branch names

## Trust These Instructions

These instructions are comprehensive and tested. Only search for additional information if:
1. Commands fail with unexpected errors
2. New dependencies are added to the project  
3. Configuration files are modified
4. You need to implement features not covered in existing codebase

For routine development, follow these instructions exactly as documented.