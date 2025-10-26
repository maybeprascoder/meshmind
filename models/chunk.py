"""Chunk model for storing text chunks and embeddings."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class ChunkMeta(BaseModel):
    """Metadata for a chunk."""
    filename: str
    size: int
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class Chunk(BaseModel):
    """Chunk model."""
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str
    file_id: str
    chunk_id: str
    text: str
    embedding: List[float]
    meta: ChunkMeta
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class ChunkCreate(BaseModel):
    """Schema for creating a new chunk."""
    user_id: str
    file_id: str
    chunk_id: str
    text: str
    embedding: List[float]
    meta: ChunkMeta


class ChunkSearchResult(BaseModel):
    """Search result for a chunk."""
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any]
