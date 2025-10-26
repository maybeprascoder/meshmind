"""Main application entry point."""
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import db_manager
from api.ingest_api import router as ingest_router
from api.query_api import router as query_router


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="MeshMind RAG API",
        description="A Python-based RAG (Retrieval Augmented Generation) system",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(ingest_router)
    app.include_router(query_router)
    
    return app


async def startup():
    """Application startup."""
    print("🚀 Starting MeshMind RAG API...")
    
    # Connect to databases
    await db_manager.connect_mongo()
    await db_manager.connect_neo4j()
    await db_manager.connect_redis()
    
    print("✅ All services connected")


async def shutdown():
    """Application shutdown."""
    print("🛑 Shutting down...")
    await db_manager.close_all()
    print("✅ Shutdown complete")


def run_ingest_api():
    """Run ingest API server."""
    app = create_app()
    
    @app.on_event("startup")
    async def startup_event():
        await startup()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        await shutdown()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
        log_level="info"
    )


def run_query_api():
    """Run query API server."""
    app = create_app()
    
    @app.on_event("startup")
    async def startup_event():
        await startup()
        print("DEBUG: Router endpoints:")
        for route in app.routes:
            print(f"  {route.methods} {route.path}")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        await shutdown()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8082,
        log_level="debug"
    )


def run_worker():
    """Run background worker."""
    from services.worker import WorkerService
    
    async def main():
        worker = WorkerService()
        await worker.start()
    
    asyncio.run(main())


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "ingest":
            run_ingest_api()
        elif command == "query":
            run_query_api()
        elif command == "worker":
            run_worker()
        else:
            print("Usage: python main.py [ingest|query|worker]")
    else:
        print("Usage: python main.py [ingest|query|worker]")
