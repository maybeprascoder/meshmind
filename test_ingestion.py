"""Test ingestion system step by step."""
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
import openai

# Load environment variables
load_dotenv()

async def test_ingestion_step_by_step():
    """Test ingestion system step by step."""
    print("Testing Ingestion System Step by Step\n")
    
    try:
        # 1. Test database connection
        print("1. Testing MongoDB connection...")
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            print("ERROR: MONGODB_URI not found in .env")
            return
        
        client = MongoClient(mongo_uri)
        db = client.brain
        
        # Test connection
        client.admin.command('ping')
        print("SUCCESS: MongoDB connected successfully")
        
        # 2. Test file reading
        print("\n2. Testing file reading...")
        with open("test-document.txt", "r", encoding="utf-8") as f:
            text = f.read()
        print(f"SUCCESS: File read: {len(text)} characters")
        
        # 3. Test chunking
        print("\n3. Testing chunking...")
        words = text.split()
        chunk_size = 50
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            chunks.append(chunk)
        print(f"SUCCESS: Created {len(chunks)} chunks")
        
        # 4. Test embeddings
        print("\n4. Testing embeddings...")
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        embeddings = []
        for i, chunk in enumerate(chunks[:2]):  # Test first 2 chunks
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=chunk
            )
            embedding = response.data[0].embedding
            embeddings.append(embedding)
            print(f"   SUCCESS: Chunk {i+1} embedded: {len(embedding)} dimensions")
        
        # 5. Test database insertion
        print("\n5. Testing database insertion...")
        
        # Insert file record
        file_doc = {
            "user_id": "u1",
            "file_id": "test-file-123",
            "filename": "test-document.txt",
            "hash": "abc123",
            "status": "completed",
            "meta": {"size": len(text)},
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        file_result = db.files.insert_one(file_doc)
        print(f"SUCCESS: File inserted: {file_result.inserted_id}")
        
        # Insert chunks
        for i, (chunk, embedding) in enumerate(zip(chunks[:2], embeddings)):
            chunk_doc = {
                "user_id": "u1",
                "file_id": "test-file-123",
                "chunk_id": f"chunk_{i}",
                "text": chunk,
                "embedding": embedding,
                "meta": {
                    "filename": "test-document.txt",
                    "size": len(chunk),
                    "tags": [],
                    "created_at": datetime.now()
                },
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            chunk_result = db.chunks.insert_one(chunk_doc)
            print(f"   SUCCESS: Chunk {i+1} inserted: {chunk_result.inserted_id}")
        
        # 6. Test retrieval
        print("\n6. Testing retrieval...")
        chunks_in_db = list(db.chunks.find({"user_id": "u1"}))
        print(f"SUCCESS: Found {len(chunks_in_db)} chunks in database")
        
        # 7. Test search
        print("\n7. Testing search...")
        query = "artificial intelligence"
        search_results = list(db.chunks.find({
            "user_id": "u1",
            "text": {"$regex": query, "$options": "i"}
        }))
        print(f"SUCCESS: Found {len(search_results)} chunks matching '{query}'")
        
        print("\nIngestion Test Complete!")
        print("SUCCESS: Database connection: Working")
        print("SUCCESS: File reading: Working")
        print("SUCCESS: Chunking: Working")
        print("SUCCESS: Embeddings: Working")
        print("SUCCESS: Database insertion: Working")
        print("SUCCESS: Search: Working")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    asyncio.run(test_ingestion_step_by_step())