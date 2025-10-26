"""Test if server is running updated code."""
import requests
import json

def test_server_code():
    """Test if server is running updated code."""
    print("Testing Server Code Version\n")
    
    base_url = "http://localhost:8082"
    headers = {"x-user-id": "u1", "Content-Type": "application/json"}
    
    try:
        # Test search with debug info
        print("1. Testing search endpoint...")
        search_data = {"query": "test", "k": 1}
        response = requests.post(f"{base_url}/api/search", 
                               headers=headers, 
                               json=search_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Test with empty query
        print("\n2. Testing with empty query...")
        search_data2 = {"query": "", "k": 1}
        response2 = requests.post(f"{base_url}/api/search", 
                                headers=headers, 
                                json=search_data2)
        print(f"Status: {response2.status_code}")
        print(f"Response: {response2.text}")
        
        # Test with non-existent query
        print("\n3. Testing with non-existent query...")
        search_data3 = {"query": "xyz123nonexistent", "k": 1}
        response3 = requests.post(f"{base_url}/api/search", 
                                headers=headers, 
                                json=search_data3)
        print(f"Status: {response3.status_code}")
        print(f"Response: {response3.text}")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_server_code()
