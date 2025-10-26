"""Add test data directly to the mock database."""
import requests
import json

BASE_URL = "http://localhost:8000"
USER_ID = "test_user_123"

def add_mock_data():
    """Add test data directly to the mock database."""
    print("Adding test data to mock database\n")
    
    # 1. Upload a file to get a file_id
    print("1. Uploading test file...")
    with open("test-kg.txt", "rb") as f:
        response = requests.post(
            f"{BASE_URL}/upload",
            headers={"user-id": USER_ID},
            files={"file": ("test-kg.txt", f)}
        )
    
    if response.status_code != 200:
        print(f"Upload failed: {response.status_code}")
        return
    
    file_id = response.json()["file_id"]
    print(f"File uploaded: {file_id}")
    
    # 2. Wait for processing to complete
    print("\n2. Waiting for processing to complete...")
    for i in range(10):
        response = requests.get(
            f"{BASE_URL}/file/{file_id}/status",
            headers={"user-id": USER_ID}
        )
        
        status = response.json().get("status")
        print(f"Status: {status}")
        
        if status == "processed":
            break
        
        import time
        time.sleep(2)
    
    # 3. Test search with direct query
    print("\n3. Testing search with direct query...")
    response = requests.post(
        f"{BASE_URL}/query",
        headers={"user-id": USER_ID, "Content-Type": "application/json"},
        json={
            "query": "Machine Learning",
            "file_id": file_id,
            "session_id": "test_session",
            "use_kg": True
        }
    )
    
    print(f"Search response: {response.status_code}")
    result = response.json()
    print(f"Sources: {len(result['sources'])}")
    
    # 4. Test debug endpoint
    print("\n4. Testing debug endpoint...")
    response = requests.post(
        f"{BASE_URL}/debug/kg",
        headers={"user-id": USER_ID, "Content-Type": "application/json"},
        json={
            "query": "Machine Learning",
            "file_id": file_id
        }
    )
    
    print(f"Debug response: {response.status_code}")
    debug_result = response.json()
    print(f"KG chunks: {debug_result['kg_chunks_count']}")
    print(f"Vector chunks: {debug_result['vector_chunks_count']}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    add_mock_data()
