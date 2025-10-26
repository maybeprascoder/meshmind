"""Test direct knowledge graph querying."""
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "test_user_123"

def test_kg_direct():
    """Test direct knowledge graph querying."""
    print("Testing Direct Knowledge Graph Querying\n")
    
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
    file_id = files[0]["file_id"]
    print(f"Using file: {file_id} ({files[0]['filename']})")
    
    # Get knowledge graph
    print("\n2. Getting knowledge graph...")
    response = requests.get(
        f"{BASE_URL}/graph/{file_id}",
        headers={"user-id": USER_ID}
    )
    
    if response.status_code != 200:
        print(f"Failed to get graph: {response.status_code}")
        return
    
    graph = response.json()
    print(f"Graph has {len(graph['nodes'])} nodes and {len(graph['edges'])} edges")
    
    # Print all entities and relationships
    print("\nEntities:")
    for node in graph["nodes"]:
        print(f"  - {node['label']} ({node['type']})")
    
    print("\nRelationships:")
    for edge in graph["edges"]:
        print(f"  - {edge['source']} -> {edge['label']} -> {edge['target']}")
    
    # Test specific entity-focused queries
    print("\n3. Testing entity-focused queries...")
    
    entity_queries = [
        "Tell me about Geoffrey Hinton",
        "What is the relationship between Deep Learning and Machine Learning?",
        "What is BERT used for?"
    ]
    
    for query in entity_queries:
        print(f"\nQuery: {query}")
        
        # Call the API directly with debug info
        response = requests.post(
            f"{BASE_URL}/query",
            headers={"user-id": USER_ID, "Content-Type": "application/json"},
            json={
                "query": query,
                "file_id": file_id,
                "session_id": "test_direct",
                "use_kg": True
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result["answer"]
            sources = result["sources"]
            
            print(f"Answer: {answer[:150]}...")
            print(f"Sources: {len(sources)}")
            
            kg_sources = [s for s in sources if s["source_type"] == "knowledge_graph"]
            vector_sources = [s for s in sources if s["source_type"] == "vector_search"]
            
            print(f"Knowledge graph sources: {len(kg_sources)}")
            print(f"Vector search sources: {len(vector_sources)}")
            
            if kg_sources:
                print("\nKnowledge graph sources:")
                for source in kg_sources:
                    print(f"  - {source['text'][:100]}...")
        else:
            print(f"Query failed: {response.status_code}")
            print(response.text)
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_kg_direct()
