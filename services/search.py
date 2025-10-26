"""Search and retrieval service."""
import os
import re
from typing import List, Dict, Any, Optional

import openai
from pymongo import MongoClient
from models.chunk import ChunkSearchResult

class SearchService:
    """Service for searching and retrieving information."""

    def __init__(self):
        print("SEARCH SERVICE: SearchService initialized!")
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.mongo_uri = os.getenv("MONGODB_URI")
        self.db_name = os.getenv("MONGODB_DB_NAME", "brain")

    def _get_db(self):
        if not self.mongo_uri:
            raise RuntimeError("MONGODB_URI is not set")
        client = MongoClient(self.mongo_uri)
        return client, client[self.db_name]

    async def search(
        self,
        user_id: str,
        query: str,
        k: int = 10,
        file_ids: Optional[List[str]] = None
    ) -> List[ChunkSearchResult]:
        print(f"SEARCH SERVICE: search(user_id='{user_id}', query='{query}', k={k}, file_ids={file_ids})")

        try:
            client, db = self._get_db()
            print(f"Connected to MongoDB db='{self.db_name}'. Collections: {db.list_collection_names()}")

            total = db.chunks.estimated_document_count()
            print(f"chunks total docs: {total}")

            # Build match filter - handle both camelCase and snake_case field names
            match: Dict[str, Any] = {}
            
            # Try both field name formats for user_id
            user_chunks_camel = db.chunks.count_documents({"userId": user_id})
            user_chunks_snake = db.chunks.count_documents({"user_id": user_id})
            print(f"User chunks (camelCase): {user_chunks_camel}")
            print(f"User chunks (snake_case): {user_chunks_snake}")
            
            if user_chunks_camel > 0:
                match["userId"] = user_id
                field_format = "camelCase"
            elif user_chunks_snake > 0:
                match["user_id"] = user_id
                field_format = "snake_case"
            else:
                print(f"No chunks found for user '{user_id}'")
                return []
            
            print(f"Using field format: {field_format}")
            
            if query:
                safe = re.escape(query)
                match["text"] = {"$regex": safe, "$options": "i"}
            if file_ids:
                if field_format == "camelCase":
                    match["fileId"] = {"$in": file_ids}
                else:
                    match["file_id"] = {"$in": file_ids}

            print(f"Mongo match filter: {match}")

            cursor = db.chunks.find(match, {"_id": 0}).limit(k)
            chunks = list(cursor)
            print(f"matched docs: {len(chunks)}")

            results: List[ChunkSearchResult] = []
            for i, ch in enumerate(chunks):
                # Handle both field name formats
                if field_format == "camelCase":
                    chunk_id = ch.get("chunkId", f"chunk-{i}")
                    file_id = ch.get("fileId", "")
                else:
                    chunk_id = ch.get("chunk_id", f"chunk-{i}")
                    file_id = ch.get("file_id", "")
                
                meta = ch.get("meta") or {}
                filename = meta.get("filename") or meta.get("file_name") or "unknown"
                
                results.append(
                    ChunkSearchResult(
                        chunk_id=chunk_id,
                        text=ch.get("text", ""),
                        score=max(0.0, 0.9 - i * 0.05),
                        metadata={
                            "filename": filename,
                            "file_id": file_id
                        }
                    )
                )

            client.close()
            print(f"returning {len(results)} results")
            return results

        except Exception as e:
            print(f"SEARCH SERVICE ERROR: {e}")
            import traceback; print(traceback.format_exc())
            return []