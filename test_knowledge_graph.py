"""Test knowledge graph creation and hybrid retrieval."""
import requests
import time
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:8000"
USER_ID = "test_user_123"

def test_knowledge_graph():
    """Test uploading a PDF, creating a knowledge graph, and querying with hybrid retrieval."""
    print("Testing Knowledge Graph Creation and Hybrid Retrieval\n")
    
    # 1. Upload PDF file
    pdf_file = "ai_analyst_newton.pdf"  # Replace with your actual PDF file name
    
    try:
        with open(pdf_file, "rb") as f:
            print(f"1. Uploading PDF: {pdf_file}")
            response = requests.post(
                f"{BASE_URL}/upload",
                headers={"user-id": USER_ID},
                files={"file": (pdf_file, f, "application/pdf")}
            )
            
            if response.status_code != 200:
                print(f"Upload failed: {response.status_code}")
                print(response.text)
                return
            
            result = response.json()
            file_id = result["file_id"]
            print(f"   File uploaded: {file_id}")
            print(f"   Status: {result['status']}\n")
        
        # 2. Check processing status (wait for knowledge graph creation)
        print("2. Checking processing status...")
        status = ""
        for i in range(30):  # Wait up to 60 seconds
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
            elif status == "building_graph":
                print("   Building knowledge graph...\n")
            
            time.sleep(2)
        else:
            print("   Processing timed out\n")
            return
        
        # 3. Get knowledge graph data
        if status == "processed":
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
                        print(f"     - {edge['source']} {edge['label']} {edge['target']}")
            else:
                print(f"   Failed to retrieve graph: {response.status_code}")
                print(f"   {response.text}")
        
        # 4. Test hybrid retrieval
        print("\n4. Testing hybrid retrieval...")
        queries = [
            "What are the main concepts discussed in this document?",
            "What is the relationship between AI and machine learning?",
            "What are the key technologies mentioned?"
        ]
        
        for query in queries:
            print(f"\n   Query: {query}")
            
            # Test with knowledge graph
            response_kg = requests.post(
                f"{BASE_URL}/query",
                headers={"user-id": USER_ID, "Content-Type": "application/json"},
                json={
                    "query": query,
                    "file_id": file_id,
                    "session_id": "test_kg",
                    "use_kg": True
                }
            )
            
            # Test without knowledge graph
            response_no_kg = requests.post(
                f"{BASE_URL}/query",
                headers={"user-id": USER_ID, "Content-Type": "application/json"},
                json={
                    "query": query,
                    "file_id": file_id,
                    "session_id": "test_no_kg",
                    "use_kg": False
                }
            )
            
            if response_kg.status_code == 200 and response_no_kg.status_code == 200:
                result_kg = response_kg.json()
                result_no_kg = response_no_kg.json()
                
                print(f"   With KG: {len(result_kg['sources'])} sources")
                print(f"   Without KG: {len(result_no_kg['sources'])} sources")
                
                print(f"   Answer with KG: {result_kg['answer'][:100]}...")
                print(f"   Answer without KG: {result_no_kg['answer'][:100]}...")
            else:
                print(f"   Query failed: KG={response_kg.status_code}, No KG={response_no_kg.status_code}")
        
        print("\nTest completed successfully!")
        
    except FileNotFoundError:
        print(f"ERROR: PDF file '{pdf_file}' not found.")
        print("Please place a PDF file in the current directory and update the filename in the script.")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_knowledge_graph()
