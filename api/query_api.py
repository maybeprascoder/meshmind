"""Query API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
from models.chunk import ChunkSearchResult
# Remove SearchService import
# from services.search import SearchService
from services.chat import ChatService
import json

router = APIRouter(prefix="/api", tags=["query"])
# Remove SearchService instantiation
# search_service = SearchService()
chat_service = ChatService()


@router.post("/search")
async def search(
    request: Dict[str, Any],
    user_id: str = "u1"
) -> List[Dict[str, Any]]:
    """Search for relevant chunks."""
    print("=== API SEARCH ENDPOINT CALLED ===")
    print(f"Request: {request}")
    print(f"User ID: {user_id}")
    
    # Return static test results
    return [
        {
            "chunk_id": "test-chunk-1",
            "text": "Artificial Intelligence is a branch of computer science that creates machines to perform human-like tasks.",
            "score": 0.9,
            "metadata": {
                "filename": "AI Guide",
                "file_id": "test-file"
            }
        },
        {
            "chunk_id": "test-chunk-2",
            "text": "Machine Learning is a subset of AI that focuses on algorithms that learn from experience.",
            "score": 0.8,
            "metadata": {
                "filename": "AI Guide",
                "file_id": "test-file"
            }
        }
    ]


@router.post("/chat")
async def chat(
    request: Dict[str, Any],
    user_id: str = "u1"
) -> Dict[str, Any]:
    """Chat with the system."""
    try:
        query = request.get("query", "")
        session_id = request.get("session_id", "default")
        result = await chat_service.chat(user_id, query, session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/stream")
async def stream_chat(
    query: str,
    session_id: str = "default",
    user_id: str = "u1"
):
    """Stream chat response."""
    try:
        async def generate():
            async for chunk in chat_service.stream_chat(user_id, query, session_id):
                yield f"data: {json.dumps(chunk)}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working."""
    print("=== TEST ENDPOINT CALLED ===")
    return {"message": "API is working!", "timestamp": "now"}


@router.post("/debug")
async def debug_endpoint(request: Dict[str, Any]):
    """Debug endpoint to see what's being received."""
    print("=== DEBUG ENDPOINT CALLED ===")
    print(f"Request: {request}")
    print(f"Request type: {type(request)}")
    return {"received": request}


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    from config.database import db_manager
    health = await db_manager.get_health_status()
    return {"service": "query-api", **health}