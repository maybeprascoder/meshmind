"""Test the simple FastAPI app."""
import requests
import json
import time
import os

# Base URL for the API
BASE_URL = "http://localhost:8000"
USER_ID = "test_user_123"

def test_health():
    """Test health endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(response.json())
    
    return response.status_code == 200

def test_upload_file():
    """Test file upload."""
    # Create a simple text file
    with open("test_upload.txt", "w") as f:
        f.write("This is a test file for upload.\n")
        f.write("It contains some text about artificial intelligence.\n")
        f.write("AI is transforming how we work and live.\n")
        f.write("Machine learning is a subset of AI focused on algorithms that learn from data.\n")
    
    # Upload the file
    with open("test_upload.txt", "rb") as f:
        response = requests.post(
            f"{BASE_URL}/upload",
            headers={"user-id": USER_ID},  # Note: Header is 'user-id', not 'user_id'
            files={"file": ("test_upload.txt", f)}
        )
    
    print(f"Upload response: {response.status_code}")
    print(response.json())
    
    if response.status_code == 200:
        file_id = response.json().get("file_id")
        return file_id
    return None

def test_file_status(file_id):
    """Test file status endpoint."""
    # Check status a few times
    for _ in range(5):
        response = requests.get(
            f"{BASE_URL}/file/{file_id}/status",
            headers={"user-id": USER_ID}  # Note: Header is 'user-id', not 'user_id'
        )
        
        print(f"Status check: {response.status_code}")
        print(response.json())
        
        status = response.json().get("status")
        if status == "processed":
            return True
        
        # Wait a bit before checking again
        time.sleep(2)
    
    return False

def test_query(file_id):
    """Test query endpoint."""
    # Query about AI
    query_data = {
        "query": "What is artificial intelligence?",
        "file_id": file_id,
        "session_id": "test_session_1"
    }
    
    response = requests.post(
        f"{BASE_URL}/query",
        headers={"user-id": USER_ID, "Content-Type": "application/json"},  # Note: Header is 'user-id', not 'user_id'
        json=query_data
    )
    
    print(f"Query response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Query about machine learning
    query_data = {
        "query": "What is machine learning?",
        "file_id": file_id,
        "session_id": "test_session_1"
    }
    
    response = requests.post(
        f"{BASE_URL}/query",
        headers={"user-id": USER_ID, "Content-Type": "application/json"},  # Note: Header is 'user-id', not 'user_id'
        json=query_data
    )
    
    print(f"Query response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    return response.status_code == 200

def test_chat_history(file_id):
    """Test chat history endpoint."""
    response = requests.get(
        f"{BASE_URL}/chat-history/{file_id}",
        headers={"user-id": USER_ID}  # Note: Header is 'user-id', not 'user_id'
    )
    
    print(f"Chat history response: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    return response.status_code == 200

def run_tests():
    """Run all tests."""
    print("Starting tests...")
    
    # Test health endpoint
    if not test_health():
        print("Health check failed. Make sure the server is running.")
        return
    
    # Test file upload
    file_id = test_upload_file()
    if not file_id:
        print("File upload failed.")
        return
    
    # Test file status
    if not test_file_status(file_id):
        print("File processing timed out or failed.")
        # Continue anyway
    
    # Test query
    if not test_query(file_id):
        print("Query failed.")
        return
    
    # Test chat history
    if not test_chat_history(file_id):
        print("Chat history retrieval failed.")
        return
    
    print("All tests completed successfully!")
    
    # Clean up
    if os.path.exists("test_upload.txt"):
        os.remove("test_upload.txt")

if __name__ == "__main__":
    run_tests()
