"""Job model for tracking background processing jobs."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class JobProgress(BaseModel):
    """Job progress tracking."""
    chunks_done: int = 0
    chunks_total: int = 0
    current_step: str = "queued"


class Job(BaseModel):
    """Job model."""
    id: Optional[str] = Field(alias="_id", default=None)
    job_id: str
    user_id: str
    file_id: str
    status: str = "queued"  # queued, processing, completed, failed
    progress: JobProgress = Field(default_factory=JobProgress)
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class JobCreate(BaseModel):
    """Schema for creating a new job."""
    job_id: str
    user_id: str
    file_id: str
    status: str = "queued"
