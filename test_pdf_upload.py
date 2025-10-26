"""Test PDF upload and processing."""
import requests
import time
import json

BASE_URL = "http://localhost:8000"
USER_ID = "test_user_123"

def test_pdf_upload():
    """Test uploading and querying a PDF file."""
    print("Testing PDF Upload and Processing\n")
    
    # 1. Upload PDF file (you need to have a PDF file to test)
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
                chunks_count = status_data.get("chunks_count", 0)
                print(f"   SUCCESS! File processed with {chunks_count} chunks\n")
                break
            elif status == "failed":
                error = status_data.get("error", "Unknown error")
                print(f"   FAILED: {error}\n")
                return
            
            time.sleep(2)
        else:
            print("   Processing timed out\n")
            return
        
        # 3. Query the PDF
        print("3. Querying the PDF...")
        queries = [
            "What is this document about?",
            "Give me a summary of the main points",
            "What are the key findings?"
        ]
        
        for query in queries:
            print(f"\n   Query: {query}")
            response = requests.post(
                f"{BASE_URL}/query",
                headers={"user-id": USER_ID, "Content-Type": "application/json"},
                json={
                    "query": query,
                    "file_id": file_id,
                    "session_id": "test_session_1"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result["answer"]
                sources = result["sources"]
                
                print(f"   Answer: {answer[:200]}...")
                print(f"   Sources: {len(sources)} chunks used")
            else:
                print(f"   Query failed: {response.status_code}")
                print(f"   {response.text}")
        
        # 4. Get chat history
        print("\n4. Getting chat history...")
        response = requests.get(
            f"{BASE_URL}/chat-history/{file_id}",
            headers={"user-id": USER_ID}
        )
        
        if response.status_code == 200:
            history = response.json()
            print(f"   Chat history has {len(history)} messages")
        
        print("\nTest completed successfully!")
        
    except FileNotFoundError:
        print(f"ERROR: PDF file '{pdf_file}' not found.")
        print("Please place a PDF file in the current directory and update the filename in the script.")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_upload()

