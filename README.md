# NewsNeuron
## Where News Meets Intelligence

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Vue 3.3+](https://img.shields.io/badge/Vue-3.3+-green.svg)](https://vuejs.org/)
[![FastAPI 0.116+](https://img.shields.io/badge/FastAPI-0.116+-red.svg)](https://fastapi.tiangolo.com/)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18+-green.svg)](https://nodejs.org/)
[![ESLint 9+](https://img.shields.io/badge/ESLint-9+-4B32C3.svg)](https://eslint.org/)

NewsNeuron is an advanced AI-powered news analysis system that combines Retrieval-Augmented Generation (RAG) with Knowledge Graph technology to deliver contextual news insights. The system processes information like interconnected neurons, understanding both content and relationships between entities.

## 🚀 Key Features

- **AI-Summarized Flashcards**: Quick news updates with intelligent summaries
- **Intelligent Q&A Chatbot**: Context-aware responses with hybrid intelligence
- **Dynamic Timeline View**: Visualize story evolution over time
- **Hybrid Intelligence**: Combines vector search with graph traversal for deeper insights

## 🏗️ Architecture

```
NewsNeuron/
├── frontend/          # Vue.js + Tailwind CSS UI
├── backend/           # FastAPI + Python backend
├── data-processing/   # Data ingestion pipeline
└── docs/             # Documentation
```

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| **Frontend** | Vue.js | 3.3+ | Reactive UI with Composition API |
| **Styling** | Tailwind CSS | 3.4+ | Utility-first CSS framework |
| **Build Tool** | Vite | 7.1+ | Fast development and build |
| **State Management** | Pinia | 2.1+ | Lightweight state management |
| **Backend API** | FastAPI | 0.116+ | High-performance async API |
| **AI Orchestration** | LangGraph | 0.6+ | Multi-agent workflow orchestration |
| **Language Models** | LangChain + OpenAI | Latest | RAG and conversation chains |
| **Vector Database** | Supabase + pgvector | Latest | Semantic search and embeddings |
| **Knowledge Graph** | Neo4j | 5.28+ | Entity relationships and graph queries |
| **Data Processing** | spaCy + pandas | Latest | NLP and data manipulation |
| **Testing** | Vitest + pytest | Latest | Frontend and backend testing |
| **Code Quality** | ESLint 9 + Black | Latest | Modern linting and formatting |
| **Deployment** | Vercel + Docker | Latest | Serverless and containerized deployment |

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18+) and npm/yarn
- **Python** (v3.10+) and pip
- **Git** (latest version)
- **Docker** (optional, for containerized development)

### Required Accounts

You'll need accounts for the following services:

- [Supabase](https://supabase.com/) - Vector database
- [Neo4j AuraDB](https://neo4j.com/cloud/aura/) - Knowledge graph
- [OpenRouter](https://openrouter.ai/) - AI model routing (optional for LLMs)
- [Vercel](https://vercel.com/) - Deployment

### 🆓 Free Embeddings

NewsNeuron uses **completely free** local embeddings by default:
- **No API costs** - Uses sentence-transformers locally
- **Lightweight** - CPU-only, 384-dimensional vectors
- **Private** - All processing stays on your server
- **Fast** - Optimized for semantic search

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/newsneuron.git
cd newsneuron
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the backend directory:

```bash
cp .env.example .env
# Edit .env with your API keys and database credentials
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

> **Note**: We've updated to ESLint 9 with flat config for modern linting. Installation should complete without deprecation warnings.

Create a `.env` file in the frontend directory:

```bash
cp env.example .env
# Edit .env with your API URLs and configuration
```

### 4. Database Setup

#### Supabase Configuration

1. Create a new Supabase project
2. Enable the pgvector extension
3. Run the SQL schema from `backend/database/supabase_schema.sql`

#### Neo4j Setup

1. Create a Neo4j AuraDB instance
2. Note your connection credentials
3. The graph schema will be created automatically during data ingestion

### 5. Run the Application

#### Backend (Terminal 1)

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

The application will be available at:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📊 Data Processing

To populate your databases with news data:

```bash
cd backend
python data-processing/ingest.py
```

This will:
1. Process news articles from your dataset
2. Generate embeddings using free local models
3. Extract entities using spaCy NER
4. Populate both Supabase and Neo4j databases

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## 📚 API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Main Endpoints

- `POST /api/chat` - AI chatbot interaction
- `GET /api/flashcards` - Retrieve news flashcards
- `GET /api/search` - Semantic search
- `GET /api/timeline/{entity}` - Entity timeline visualization

## 🚀 Deployment

### Vercel Deployment

1. Install Vercel CLI: `npm i -g vercel`
2. Login: `vercel login`
3. Deploy: `vercel --prod`

### Environment Variables

Make sure to set the following environment variables in your deployment:

**Backend (.env)**
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
OPENROUTER_API_KEY=your_openrouter_api_key
```

**Frontend (.env)**
```
VITE_API_BASE_URL=https://your-backend-url.vercel.app
```

## 👥 Development Team

- **HARI** - Project Lead & Backend Architecture
- **VARADA** - Frontend Development & UI/UX
- **SANJAI** - AI Agent & LangGraph Integration
- **ARYA** - Data Processing & Database Design
- **KOHIL** - DevOps & Deployment

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔮 Future Enhancements

- **Caching Layer**: Redis implementation for performance
- **Real-time Updates**: WebSocket support for live news feeds
- **Multi-language Support**: Extend to non-English sources
- **Mobile App**: React Native companion
- **Advanced Analytics**: Sentiment analysis and trend prediction

## 📞 Support

If you encounter any issues or have questions, please:

1. Check the [documentation](docs/)
2. Search existing [issues](https://github.com/yourusername/newsneuron/issues)
3. Create a new issue if needed

---

**NewsNeuron** - Transforming how we understand and interact with news through AI-powered intelligence.
