# NewsNeuron Setup Guide

This guide will help you set up and run the NewsNeuron project locally.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher)
- **Git**
- **Docker** and **Docker Compose** (optional, for containerized setup)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/newsneuron.git
cd newsneuron
```

### 2. Environment Setup

#### Backend Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Create environment file:
```bash
cp env.example .env
# Edit .env with your configuration
```

#### Frontend Environment

```bash
cd ../frontend
npm install
```

> **✅ Modern Setup**: We've updated to ESLint 9 with flat config for better performance and modern JavaScript support. Installation should complete without deprecation warnings.

Create environment file:
```bash
cp env.example .env
# Edit .env with your configuration
```

### 3. Database Setup

You have two options for database setup:

#### Option A: Using Docker (Recommended)

```bash
# Start databases only
docker-compose up postgres neo4j redis -d

# Wait for databases to be ready, then run schema setup
cd backend
python -c "
from app.database.supabase_client import get_supabase_client
from app.database.neo4j_client import get_neo4j_client
print('Databases connected successfully')
"
```

#### Option B: Using Supabase Cloud and Neo4j AuraDB

1. Create a [Supabase](https://supabase.com/) project
2. Create a [Neo4j AuraDB](https://neo4j.com/cloud/aura/) instance
3. Update your `.env` files with the connection details
4. Run the SQL schema in your Supabase project:
   ```bash
   # Copy the contents of backend/database/supabase_schema.sql
   # and run it in your Supabase SQL editor
   ```

### 4. Run the Application

#### Development Mode

Terminal 1 (Backend):
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

#### Using Docker Compose

```bash
# Development mode
docker-compose up

# Production mode
docker-compose --profile production up
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (if using Docker)

## Data Ingestion

To populate your databases with sample news data:

```bash
cd backend
source venv/bin/activate
python data-processing/ingest.py
```

This will:
1. Create sample news articles
2. Extract entities using spaCy NER
3. Generate embeddings using OpenAI
4. Populate both Supabase and Neo4j databases

## Configuration

### Environment Variables

#### Backend (.env)
```
# Database Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
NEO4J_URI=your_neo4j_uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_neo4j_password

# AI Services
OPENAI_API_KEY=your_openai_api_key
OPENROUTER_API_KEY=your_openrouter_api_key

# Application Settings
DEBUG=True
SECRET_KEY=your_secret_key
```

#### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME=NewsNeuron
VITE_ENABLE_DEBUG=true
```

## Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### Linting and Code Quality

#### Frontend (ESLint 9 + Prettier)
```bash
cd frontend
npm run lint        # ESLint 9 with flat config
npm run format      # Prettier formatting
```

#### Backend (Black + flake8)
```bash
cd backend
black . --check     # Code formatting check
flake8 .           # Linting
black .            # Apply formatting
```

> **Note**: Frontend now uses ESLint 9 with modern flat config format (`eslint.config.js`) for better performance and configuration clarity.

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   # Kill the process or use a different port
   ```

2. **Database Connection Issues**
   - Ensure your database credentials are correct
   - Check if databases are running (`docker-compose ps`)
   - Verify network connectivity

3. **Module Import Errors**
   - Ensure virtual environment is activated
   - Install missing dependencies: `pip install -r requirements.txt`

4. **spaCy Model Not Found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Frontend Build Issues**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

6. **ESLint Deprecation Warnings** (Fixed in Latest Version)
   ```bash
   # Our setup now uses ESLint 9 with flat config
   # No more deprecation warnings during npm install
   npm run lint  # Modern linting with flat config
   ```

7. **Package Conflicts**
   ```bash
   # Clear npm cache if needed
   npm cache clean --force
   ```

### Performance Optimization

1. **Database Indexing**
   - Ensure proper indexes are created (see schema files)
   - Monitor query performance

2. **API Response Times**
   - Enable caching with Redis
   - Optimize vector search parameters

3. **Frontend Performance**
   - Enable production build optimizations
   - Implement code splitting for large bundles

## Development Workflow

1. Create a new branch for your feature
2. Make your changes
3. Run tests locally
4. Commit with descriptive messages
5. Push and create a pull request

## Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment instructions.

## Getting Help

- Check the [FAQ](./FAQ.md)
- Review existing [Issues](https://github.com/yourusername/newsneuron/issues)
- Join our community discussions

## Next Steps

- Set up your development environment
- Run the data ingestion pipeline
- Explore the API documentation
- Start building features!

For more detailed information, see the individual component documentation:
- [Backend Documentation](../backend/README.md)
- [Frontend Documentation](../frontend/README.md)
- [Database Schema](./DATABASE.md)
