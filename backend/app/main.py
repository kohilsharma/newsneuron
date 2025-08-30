"""
NewsNeuron FastAPI Application
Main entry point for the NewsNeuron backend API
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio

from app.config import settings
from app.routers import chat, flashcards, search, timeline
from app.database.supabase_client import get_supabase_client
from app.database.neo4j_client import get_neo4j_driver
from app.services.embedding_service import initialize_embedding_service

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


@app.on_event("startup")
async def startup_event():
    """Fast startup - only initialize critical services"""
    print("🚀 Starting NewsNeuron backend...")

    # Fast startup - skip heavy initialization
    # Services will be initialized lazily on first use
    print("✅ Fast startup complete - services will initialize on demand")

    # Start background initialization for heavy services (non-blocking)
    background_tasks = BackgroundTasks()
    background_tasks.add_task(initialize_heavy_services_async)
    print("🎉 NewsNeuron backend ready!")


async def initialize_heavy_services_async():
    """Initialize heavy services in background after startup"""
    try:
        print("🔄 Starting background service initialization...")

        # Initialize embedding service in background
        try:
            print("📦 Initializing embedding service...")
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, initialize_embedding_service)
            if success:
                print("✅ Embedding service initialized")
            else:
                print("⚠️ Embedding service initialization failed")
        except Exception as e:
            print(f"⚠️ Warning: Embedding service initialization failed: {e}")

        # Test database connections (optional, only if configured)
        if settings.supabase_url and settings.supabase_anon_key:
            try:
                print("🔗 Testing Supabase connection...")
                supabase = get_supabase_client()
                if supabase and supabase.get_client():
                    print("✅ Supabase connected")
                else:
                    print("⚠️ Supabase not configured")
            except Exception as e:
                print(f"⚠️ Supabase connection failed: {e}")

        if settings.neo4j_uri and settings.neo4j_password:
            try:
                driver = get_neo4j_driver()
                if driver:
                    with driver.session() as session:
                        result = session.run("RETURN 1 as test")
                        if result.single():
                            print("✅ Neo4j connected")
                        else:
                            print("⚠️ Neo4j connection failed")
                else:
                    print("⚠️ Neo4j not configured")
            except Exception as e:
                print(f"⚠️ Neo4j connection failed: {e}")

        print("🎯 Background initialization complete")

    except Exception as e:
        print(f"⚠️ Background initialization error: {e}")


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
    """Fast health check endpoint"""
    try:
        # Fast health check - just return basic status
        # Database connections are tested in background
        return {
            "status": "healthy",
            "app_name": settings.app_name,
            "version": settings.app_version,
            "startup_mode": "fast",
            "databases": {
                "supabase": "checking_in_background" if settings.supabase_url else "not_configured",
                "neo4j": "checking_in_background" if settings.neo4j_uri else "not_configured"
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


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with full database testing"""
    try:
        # Test database connections (expensive operation)
        supabase = get_supabase_client()
        driver = get_neo4j_driver()

        # Basic connectivity tests
        supabase_status = "connected" if supabase and supabase.get_client() else "disconnected"

        # Test Neo4j connection
        try:
            if driver:
                with driver.session() as session:
                    result = session.run("RETURN 1 as test")
                    neo4j_status = "connected" if result.single() else "disconnected"
            else:
                neo4j_status = "disconnected"
        except Exception:
            neo4j_status = "disconnected"

        return {
            "status": "healthy" if supabase_status == "connected" or neo4j_status == "connected" else "degraded",
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
    print(f"❌ Unhandled exception: {str(exc)}")
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
        reload=settings.debug,
        log_level="info"
    )
