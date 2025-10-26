"""Test the knowledge graph debug endpoint."""
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "test_user_123"

def test_kg_debug():
    """Test the knowledge graph debug endpoint."""
    print("Testing Knowledge Graph Debug Endpoint\n")
    
    # Get list of files
    print("1. Getting list of files...")
    response = requests.get(
        f"{BASE_URL}/files",
        headers={"user-id": USER_ID}
    )
    
    if response.status_code != 200:
        print(f"Failed to get files: {response.status_code}")
        return
    
    files = response.json()
    print(f"Found {len(files)} files")
    
    if not files:
        print("No files found. Please run test_kg_simple.py first.")
        return
    
    # Use the most recent file
    # Sort files by creation time (most recent first)
    files.sort(key=lambda f: f.get("created_at", ""), reverse=True)
    file_id = files[0]["file_id"]
    print(f"Using file: {file_id} ({files[0]['filename']})")
    
    # Test specific entity-focused queries
    print("\n2. Testing entity-focused queries with debug endpoint...")
    
    entity_queries = [
        "Tell me about Geoffrey Hinton",
        "What is the relationship between Deep Learning and Machine Learning?",
        "What is BERT used for?"
    ]
    
    for query in entity_queries:
        print(f"\nQuery: {query}")
        
        # Call the debug endpoint
        response = requests.post(
            f"{BASE_URL}/debug/kg",
            headers={"user-id": USER_ID, "Content-Type": "application/json"},
            json={
                "query": query,
                "file_id": file_id
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"Knowledge graph chunks: {result['kg_chunks_count']}")
            if result['kg_chunks']:
                for i, chunk in enumerate(result['kg_chunks']):
                    print(f"  {i+1}. {chunk['text']}")
            
            print(f"Vector search chunks: {result['vector_chunks_count']}")
            if result['vector_chunks']:
                for i, chunk in enumerate(result['vector_chunks']):
                    print(f"  {i+1}. {chunk['text']}")
        else:
            print(f"Debug query failed: {response.status_code}")
            print(response.text)
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_kg_debug()
