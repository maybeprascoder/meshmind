"""File ingestion service."""
import asyncio
import os
from typing import List, Dict, Any
from config.database import db_manager
from models.chunk import Chunk, ChunkCreate, ChunkMeta
from models.file import File, FileCreate
from models.job import Job, JobCreate, JobProgress


class IngestService:
    """Service for ingesting and processing files."""
    
    def __init__(self):
        import openai
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    async def register_file(self, file_data: FileCreate) -> str:
        """Register a new file for processing."""
        # Create file record
        file_doc = File(**file_data.dict())
        await db_manager.mongo_client.brain.files.insert_one(file_doc.dict())
        
        # Create job
        job_id = f"job_{file_data.file_id}_{file_data.user_id}"
        job_data = JobCreate(
            job_id=job_id,
            user_id=file_data.user_id,
            file_id=file_data.file_id
        )
        job_doc = Job(**job_data.dict())
        await db_manager.mongo_client.brain.jobs.insert_one(job_doc.dict())
        
        # Queue for processing
        await self._queue_job(job_id, file_data.dict())
        
        return job_id
    
    async def process_file(self, job_id: str, file_data: Dict[str, Any]):
        """Process a file and create chunks."""
        try:
            # Update job status
            await self._update_job_status(job_id, "processing", "parsing")
            
            # Load document
            if file_data.get("s3_key"):
                # TODO: Load from S3
                text = "Sample text content"
            else:
                # Load from local file
                with open(file_data["filename"], "r", encoding="utf-8") as f:
                    text = f.read()
            
            # Split into chunks
            await self._update_job_status(job_id, "processing", "chunking")
            words = text.split()
            chunk_size = 50
            chunks = []
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i+chunk_size])
                chunks.append(chunk)
            
            # Update progress
            await self._update_job_progress(job_id, 0, len(chunks))
            
            # Create embeddings and save chunks
            await self._update_job_status(job_id, "processing", "embedding")
            for i, chunk_text in enumerate(chunks):
                # Create embedding
                import openai
                response = openai.embeddings.create(
                    model="text-embedding-3-small",
                    input=chunk_text
                )
                embedding = response.data[0].embedding
                
                # Create chunk
                chunk_data = ChunkCreate(
                    user_id=file_data["user_id"],
                    file_id=file_data["file_id"],
                    chunk_id=f"chunk_{i}",
                    text=chunk_text,
                    embedding=embedding,
                    meta=ChunkMeta(
                        filename=file_data["filename"],
                        size=len(chunk_text)
                    )
                )
                
                # Save chunk
                chunk_doc = Chunk(**chunk_data.dict())
                await db_manager.mongo_client.brain.chunks.insert_one(chunk_doc.dict())
                
                # Update progress
                await self._update_job_progress(job_id, i + 1, len(chunks))
            
            # Complete job
            await self._update_job_status(job_id, "completed", "done")
            
        except Exception as e:
            await self._update_job_status(job_id, "failed", error=str(e))
    
    async def _queue_job(self, job_id: str, file_data: Dict[str, Any]):
        """Queue a job for processing."""
        # TODO: Implement Celery task queue
        # For now, process immediately
        await self.process_file(job_id, file_data)
    
    async def _update_job_status(self, job_id: str, status: str, current_step: str = None, error: str = None):
        """Update job status."""
        update_data = {"status": status, "updated_at": datetime.now()}
        if current_step:
            update_data["progress.current_step"] = current_step
        if error:
            update_data["error"] = error
        
        await db_manager.mongo_client.brain.jobs.update_one(
            {"job_id": job_id},
            {"$set": update_data}
        )
    
    async def _update_job_progress(self, job_id: str, chunks_done: int, chunks_total: int):
        """Update job progress."""
        await db_manager.mongo_client.brain.jobs.update_one(
            {"job_id": job_id},
            {"$set": {
                "progress.chunks_done": chunks_done,
                "progress.chunks_total": chunks_total,
                "updated_at": datetime.now()
            }}
        )
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status."""
        job = await db_manager.mongo_client.brain.jobs.find_one({"job_id": job_id})
        if job:
            job["_id"] = str(job["_id"])
            return job
        return None
