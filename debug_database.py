"""Debug database contents."""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def debug_database():
    """Check what's in the database."""
    print("Debugging Database Contents\n")
    
    try:
        # Connect to MongoDB
        mongo_uri = os.getenv("MONGODB_URI")
        client = MongoClient(mongo_uri)
        db = client.brain
        
        # Check collections
        print("Collections:", db.list_collection_names())
        
        # Check chunks
        chunks = list(db.chunks.find({"user_id": "u1"}))
        print(f"\nChunks for user u1: {len(chunks)}")
        for chunk in chunks:
            print(f"  - {chunk['chunk_id']}: {chunk['text'][:50]}...")
        
        # Check files
        files = list(db.files.find({"user_id": "u1"}))
        print(f"\nFiles for user u1: {len(files)}")
        for file in files:
            print(f"  - {file['file_id']}: {file['filename']}")
        
        # Test search query
        print(f"\nTesting search for 'artificial intelligence':")
        search_results = list(db.chunks.find({
            "user_id": "u1",
            "text": {"$regex": "artificial intelligence", "$options": "i"}
        }))
        print(f"Found {len(search_results)} results")
        for result in search_results:
            print(f"  - {result['chunk_id']}: {result['text'][:100]}...")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    debug_database()
