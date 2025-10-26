"""Test MongoDB connection directly."""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

def test_mongo_direct():
    """Test MongoDB connection directly."""
    print("Testing MongoDB Connection Directly\n")
    
    try:
        load_dotenv()
        mongo_uri = os.getenv("MONGODB_URI")
        print(f"MongoDB URI: {mongo_uri[:20] if mongo_uri else 'None'}...")
        
        client = MongoClient(mongo_uri)
        db = client.brain
        
        print(f"Connected to database: {db.name}")
        print(f"Collections: {db.list_collection_names()}")
        
        # Count total chunks
        total_chunks = db.chunks.count_documents({})
        print(f"Total chunks: {total_chunks}")
        
        # Count user chunks (both formats)
        user_id = "u1"
        user_chunks_camel = db.chunks.count_documents({"userId": user_id})
        user_chunks_snake = db.chunks.count_documents({"user_id": user_id})
        print(f"Chunks for user '{user_id}' (camelCase): {user_chunks_camel}")
        print(f"Chunks for user '{user_id}' (snake_case): {user_chunks_snake}")
        
        # Get all chunks for user (camelCase)
        chunks = list(db.chunks.find({"userId": user_id}))
        print(f"Found {len(chunks)} chunks for user '{user_id}'")
        
        for i, chunk in enumerate(chunks):
            print(f"\nChunk {i+1}:")
            print(f"  ID: {chunk.get('chunkId', 'NO_ID')}")
            print(f"  Text: {chunk.get('text', 'NO_TEXT')[:100]}...")
            print(f"  Meta: {chunk.get('meta', {})}")
        
        client.close()
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mongo_direct()
