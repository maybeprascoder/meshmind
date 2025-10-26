"""Test the simplified knowledge graph approach."""
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "test_user_123"

def test_simplified_kg():
    """Test the simplified knowledge graph approach."""
    print("Testing Simplified Knowledge Graph Approach\n")
    
    # 1. Upload a test file
    print("1. Uploading test file...")
    with open("test-kg.txt", "rb") as f:
        response = requests.post(
            f"{BASE_URL}/upload",
            headers={"user-id": USER_ID},
            files={"file": ("test-kg.txt", f)}
        )
    
    if response.status_code != 200:
        print(f"Upload failed: {response.status_code}")
        print(response.text)
        return
    
    file_id = response.json()["file_id"]
    print(f"File uploaded: {file_id}")
    
    # 2. Wait for processing to complete
    print("\n2. Waiting for processing to complete...")
    for i in range(15):  # Wait up to 30 seconds
        response = requests.get(
            f"{BASE_URL}/file/{file_id}/status",
            headers={"user-id": USER_ID}
        )
        
        status = response.json().get("status")
        print(f"Status: {status}")
        
        if status == "processed":
            print(f"Processing complete with {response.json().get('chunks_count', 0)} chunks")
            print(f"Knowledge graph: {response.json().get('entities_count', 0)} entities, {response.json().get('relationships_count', 0)} relationships")
            break
        elif status == "failed":
            print(f"Processing failed: {response.json().get('error', 'Unknown error')}")
            return
        
        import time
        time.sleep(2)
    
    # 3. Test queries with knowledge graph
    print("\n3. Testing queries with knowledge graph...")
    test_queries = [
        "What is Machine Learning?",
        "Tell me about Geoffrey Hinton",
        "What is the relationship between Deep Learning and Machine Learning?",
        "What is BERT used for?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        # Test with knowledge graph
        response = requests.post(
            f"{BASE_URL}/query",
            headers={"user-id": USER_ID, "Content-Type": "application/json"},
            json={
                "query": query,
                "file_id": file_id,
                "session_id": "test_kg",
                "use_kg": True
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Count sources by type
            kg_sources = [s for s in result["sources"] if s.get("source_type") == "knowledge_graph"]
            vector_sources = [s for s in result["sources"] if s.get("source_type") == "vector_search"]
            
            print(f"Answer: {result['answer'][:100]}...")
            print(f"Knowledge graph sources: {len(kg_sources)}")
            print(f"Vector search sources: {len(vector_sources)}")
            
            # Print the sources
            print("\nSources:")
            for i, source in enumerate(result["sources"]):
                print(f"  {i+1}. [{source['source_type']}] {source['text'][:100]}...")
        else:
            print(f"Query failed: {response.status_code}")
            print(response.text)
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_simplified_kg()
