"""Background worker service."""
import asyncio
from typing import Dict, Any
from services.ingest import IngestService


class WorkerService:
    """Service for background processing."""
    
    def __init__(self):
        self.ingest_service = IngestService()
        self.running = False
    
    async def start(self):
        """Start the worker."""
        self.running = True
        print("🔄 Worker started")
        
        while self.running:
            try:
                # TODO: Implement Celery task processing
                # For now, just wait
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Worker error: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop the worker."""
        self.running = False
        print("🛑 Worker stopped")
    
    async def process_job(self, job_id: str, file_data: Dict[str, Any]):
        """Process a specific job."""
        await self.ingest_service.process_file(job_id, file_data)
