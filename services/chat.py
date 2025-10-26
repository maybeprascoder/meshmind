"""Chat and Q&A service."""
import openai
import os
from typing import List, Dict, Any, Optional
from config.database import db_manager
from services.search import SearchService


class ChatService:
    """Service for chat and Q&A functionality."""
    
    def __init__(self):
        self.search_service = SearchService()
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    async def chat(self, user_id: str, query: str, session_id: str = "default") -> Dict[str, Any]:
        """Process a chat query."""
        try:
            # Get relevant chunks
            search_results = await self.search_service.search(user_id, query, k=5)
            
            if not search_results:
                return {
                    "answer": "I don't have enough context to answer that question. Please upload some documents first.",
                    "sources": [],
                    "session_id": session_id
                }
            
            # Create context from search results
            context = "\n\n".join([result.text for result in search_results])
            
            # Generate answer using LLM
            prompt = f"""Based on the following context, answer the user's question.

Context:
{context}

Question: {query}

Answer:"""
            
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0
            )
            answer_text = response.choices[0].message.content.strip()
            
            # Prepare sources
            sources = []
            for result in search_results:
                sources.append({
                    "chunk_id": result.chunk_id,
                    "filename": result.metadata.get("filename", "unknown"),
                    "file_id": result.metadata.get("file_id", "unknown"),
                    "score": result.score,
                    "preview": result.text[:200] + "..." if len(result.text) > 200 else result.text
                })
            
            return {
                "answer": answer_text,
                "sources": sources,
                "session_id": session_id,
                "query": query
            }
            
        except Exception as e:
            print(f"Chat error: {e}")
            return {
                "answer": "Sorry, I encountered an error processing your question.",
                "sources": [],
                "session_id": session_id,
                "error": str(e)
            }
    
    async def stream_chat(self, user_id: str, query: str, session_id: str = "default"):
        """Stream chat response."""
        try:
            # Get relevant chunks
            search_results = await self.search_service.search(user_id, query, k=5)
            
            if not search_results:
                yield {
                    "type": "error",
                    "data": "I don't have enough context to answer that question."
                }
                return
            
            # Create context
            context = "\n\n".join([result.text for result in search_results])
            
            # Generate streaming response
            prompt = f"""Based on the following context, answer the user's question.

Context:
{context}

Question: {query}

Answer:"""
            
            # Stream the response (simplified for now)
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0
            )
            
            # For now, just yield the complete response
            answer_text = response.choices[0].message.content.strip()
            yield {
                "type": "token",
                "data": answer_text
            }
            
            # Send final sources
            sources = []
            for result in search_results:
                sources.append({
                    "chunk_id": result.chunk_id,
                    "filename": result.metadata.get("filename", "unknown"),
                    "file_id": result.metadata.get("file_id", "unknown"),
                    "score": result.score
                })
            
            yield {
                "type": "done",
                "data": {
                    "sources": sources,
                    "session_id": session_id
                }
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "data": f"Error: {str(e)}"
            }
