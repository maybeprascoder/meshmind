"""Test knowledge graph creation with a simple text file."""
import requests
import time
import json

BASE_URL = "http://localhost:8000"
USER_ID = "test_user_123"

def test_kg_simple():
    """Test knowledge graph creation with a simple text file."""
    print("Testing Knowledge Graph Creation with Simple Text File\n")
    
    # 1. Upload text file
    text_file = "test-kg.txt"
    
    try:
        with open(text_file, "rb") as f:
            print(f"1. Uploading text file: {text_file}")
            response = requests.post(
                f"{BASE_URL}/upload",
                headers={"user-id": USER_ID},
                files={"file": (text_file, f)}
            )
            
            if response.status_code != 200:
                print(f"Upload failed: {response.status_code}")
                print(response.text)
                return
            
            result = response.json()
            file_id = result["file_id"]
            print(f"   File uploaded: {file_id}")
            print(f"   Status: {result['status']}\n")
        
        # 2. Check processing status
        print("2. Checking processing status...")
        for i in range(20):  # Wait up to 40 seconds
            response = requests.get(
                f"{BASE_URL}/file/{file_id}/status",
                headers={"user-id": USER_ID}
            )
            
            status_data = response.json()
            status = status_data.get("status")
            print(f"   Attempt {i+1}: Status = {status}")
            
            if status == "processed":
                entities_count = status_data.get("entities_count", 0)
                relationships_count = status_data.get("relationships_count", 0)
                print(f"   SUCCESS! File processed with:")
                print(f"     - {status_data.get('chunks_count', 0)} chunks")
                print(f"     - {entities_count} entities")
                print(f"     - {relationships_count} relationships\n")
                break
            elif status == "failed":
                error = status_data.get("error", "Unknown error")
                print(f"   FAILED: {error}\n")
                return
            
            time.sleep(2)
        
        # 3. Get knowledge graph
        print("3. Retrieving knowledge graph...")
        response = requests.get(
            f"{BASE_URL}/graph/{file_id}",
            headers={"user-id": USER_ID}
        )
        
        if response.status_code == 200:
            graph_data = response.json()
            print(f"   Graph contains {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} edges")
            
            # Print some sample nodes
            if graph_data["nodes"]:
                print("\n   Sample entities:")
                for node in graph_data["nodes"][:5]:
                    print(f"     - {node['label']} ({node['type']})")
            
            # Print some sample relationships
            if graph_data["edges"]:
                print("\n   Sample relationships:")
                for edge in graph_data["edges"][:5]:
                    print(f"     - {edge['source']} -> {edge['label']} -> {edge['target']}")
        
        # 4. Test queries
        print("\n4. Testing queries...")
        queries = [
            "What is Machine Learning?",
            "Who are the key AI researchers?",
            "What is the relationship between AI and Machine Learning?"
        ]
        
        for query in queries:
            print(f"\n   Query: {query}")
            response = requests.post(
                f"{BASE_URL}/query",
                headers={"user-id": USER_ID, "Content-Type": "application/json"},
                json={
                    "query": query,
                    "file_id": file_id,
                    "session_id": "test_session",
                    "use_kg": True
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Answer: {result['answer'][:200]}...")
                print(f"   Sources: {len(result['sources'])}")
                
                # Print source types
                kg_sources = [s for s in result['sources'] if s.get('source_type') == 'knowledge_graph']
                vector_sources = [s for s in result['sources'] if s.get('source_type') == 'vector_search']
                print(f"   Knowledge graph sources: {len(kg_sources)}")
                print(f"   Vector search sources: {len(vector_sources)}")
            else:
                print(f"   Query failed: {response.status_code}")
                print(f"   {response.text}")
        
        print("\nTest completed!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_kg_simple()
