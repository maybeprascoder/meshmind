"""File model for tracking uploaded files."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class File(BaseModel):
    """File model."""
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str
    file_id: str
    filename: str
    s3_key: Optional[str] = None
    external_id: Optional[str] = None
    hash: str
    status: str = "queued"  # queued, processing, completed, failed
    meta: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class FileCreate(BaseModel):
    """Schema for creating a new file."""
    user_id: str
    file_id: str
    filename: str
    s3_key: Optional[str] = None
    external_id: Optional[str] = None
    hash: str
    meta: Dict[str, Any] = Field(default_factory=dict)
