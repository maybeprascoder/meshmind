"""Test the /files endpoint."""
import requests

def test_files():
    """Test the /files endpoint."""
    print("Testing /files endpoint")
    
    response = requests.get(
        "http://localhost:8000/files",
        headers={"user-id": "test_user_123"}
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == "__main__":
    test_files()
