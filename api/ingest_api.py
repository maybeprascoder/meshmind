"""Ingest API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from models.file import FileCreate
from services.ingest import IngestService

router = APIRouter(prefix="/api/ingest", tags=["ingest"])
ingest_service = IngestService()


@router.post("/register")
async def register_file(file_data: FileCreate, user_id: str = "u1") -> Dict[str, Any]:
    """Register a file for processing."""
    try:
        file_data.user_id = user_id
        job_id = await ingest_service.register_file(file_data)
        return {"job_id": job_id, "status": "queued"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """Get job status."""
    try:
        status = await ingest_service.get_job_status(job_id)
        if not status:
            raise HTTPException(status_code=404, detail="Job not found")
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    from config.database import db_manager
    health = await db_manager.get_health_status()
    return {"service": "ingest-api", **health}
