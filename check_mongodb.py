"""Check what's actually in MongoDB."""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def check_mongodb():
    """Check MongoDB contents."""
    print("Checking MongoDB Contents\n")
    
    try:
        mongo_uri = os.getenv("MONGODB_URI")
        client = MongoClient(mongo_uri)
        
        # Check different database names
        for db_name in ["brain", "meshmind", "test"]:
            try:
                db = client[db_name]
                count = db.chunks.count_documents({})
                print(f"Database '{db_name}': {count} chunks")
                
                if count > 0:
                    # Show sample document
                    sample = db.chunks.find_one()
                    print(f"  Sample document: {sample}")
                    print(f"  User IDs in DB: {db.chunks.distinct('user_id')}")
                    print(f"  Collections: {db.list_collection_names()}")
                    print()
            except Exception as e:
                print(f"Database '{db_name}': Error - {e}")
        
        client.close()
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_mongodb()
