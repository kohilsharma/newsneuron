"""
NewsNeuron FastAPI Application
Main entry point for the NewsNeuron backend API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.config import settings
from app.routers import chat, flashcards, search, timeline
from app.database.supabase_client import get_supabase_client
from app.database.neo4j_client import get_neo4j_driver

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered news analysis system with hybrid vector-graph intelligence",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    chat.router,
    prefix=settings.api_v1_str + "/chat",
    tags=["chat"]
)
app.include_router(
    flashcards.router,
    prefix=settings.api_v1_str + "/flashcards",
    tags=["flashcards"]
)
app.include_router(
    search.router,
    prefix=settings.api_v1_str + "/search",
    tags=["search"]
)
app.include_router(
    timeline.router,
    prefix=settings.api_v1_str + "/timeline",
    tags=["timeline"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connections
        supabase = get_supabase_client()
        driver = get_neo4j_driver()
        
        # Basic connectivity tests
        supabase_status = "connected" if supabase else "disconnected"
        
        # Test Neo4j connection
        try:
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                neo4j_status = "connected" if result.single() else "disconnected"
        except Exception:
            neo4j_status = "disconnected"
        
        return {
            "status": "healthy",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "databases": {
                "supabase": supabase_status,
                "neo4j": neo4j_status
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "message": "Internal server error",
                "detail": str(exc)
            }
        )
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
