import streamlit as st
import requests
import time
import os
from typing import List, Dict

# Configuration
API_BASE_URL = "http://localhost:8000"
USER_ID = "streamlit_user"

# Page config
st.set_page_config(
    page_title="Document Chat",
    page_icon="📄",
    layout="wide"
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_file_id" not in st.session_state:
    st.session_state.current_file_id = None
if "current_filename" not in st.session_state:
    st.session_state.current_filename = None

def upload_file(file) -> Dict:
    """Upload file to the API."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        headers = {"user-id": USER_ID}
        
        response = requests.post(
            f"{API_BASE_URL}/upload",
            files=files,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Upload failed: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Upload error: {str(e)}")
        return None

def get_file_status(file_id: str) -> Dict:
    """Get file processing status."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/file/{file_id}/status",
            headers={"user-id": USER_ID}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error"}
    except:
        return {"status": "error"}

def query_document(query: str, file_id: str, use_kg: bool = True) -> Dict:
    """Query the document."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            headers={"user-id": USER_ID},
            json={
                "query": query,
                "file_id": file_id,
                "session_id": "streamlit_session",
                "use_kg": use_kg
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"answer": f"Query failed: {response.status_code}", "sources": []}
    except Exception as e:
        return {"answer": f"Query error: {str(e)}", "sources": []}

def get_user_files() -> List[Dict]:
    """Get list of user's files."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/files",
            headers={"user-id": USER_ID}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except:
        return []

# Main UI
st.title("📄 Document Chat")
st.markdown("Upload a document and chat with it using AI!")

# Sidebar for file management
with st.sidebar:
    st.header("📁 File Management")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload a PDF or text file",
        type=['pdf', 'txt'],
        help="Upload your document to start chatting"
    )
    
    if uploaded_file is not None:
        if st.button("Upload File", type="primary"):
            with st.spinner("Uploading file..."):
                result = upload_file(uploaded_file)
                
            if result:
                st.success(f"✅ File uploaded successfully!")
                st.session_state.current_file_id = result["file_id"]
                st.session_state.current_filename = result["filename"]
                st.session_state.chat_history = []  # Clear chat history for new file
                st.rerun()
    
    # File selection
    st.subheader("📋 Your Files")
    files = get_user_files()
    
    if files:
        file_options = {f"{f['filename']} ({f['status']})": f['file_id'] for f in files}
        selected_file = st.selectbox(
            "Select a file to chat with:",
            options=list(file_options.keys()),
            index=0 if not st.session_state.current_file_id else None
        )
        
        if selected_file:
            file_id = file_options[selected_file]
            filename = selected_file.split(" (")[0]
            
            if file_id != st.session_state.current_file_id:
                st.session_state.current_file_id = file_id
                st.session_state.current_filename = filename
                st.session_state.chat_history = []  # Clear chat history
                st.rerun()
    else:
        st.info("No files uploaded yet. Upload a file to get started!")

# Main chat area
if st.session_state.current_file_id:
    # Check file status
    file_status = get_file_status(st.session_state.current_file_id)
    
    if file_status["status"] == "processed":
        st.success(f"✅ {st.session_state.current_filename} is ready for chat!")
        
        # Chat interface
        st.subheader(f"💬 Chat with {st.session_state.current_filename}")
        
        # Display chat history
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    
                    # Show sources if available
                    if "sources" in message and message["sources"]:
                        with st.expander("📚 Sources"):
                            for j, source in enumerate(message["sources"][:3]):
                                st.write(f"**Source {j+1}:** {source['text'][:200]}...")
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your document..."):
            # Add user message to history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = query_document(prompt, st.session_state.current_file_id)
                
                answer = response.get("answer", "Sorry, I couldn't generate a response.")
                st.write(answer)
                
                # Show sources
                sources = response.get("sources", [])
                if sources:
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(sources[:3]):
                            source_type = source.get("source_type", "unknown")
                            st.write(f"**Source {i+1}** ({source_type}): {source['text'][:200]}...")
                
                # Add assistant message to history
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": answer,
                    "sources": sources
                })
    
    elif file_status["status"] == "processing":
        st.info(f"⏳ {st.session_state.current_filename} is being processed...")
        
        # Show processing progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Poll for status updates
        for i in range(30):  # Wait up to 30 seconds
            file_status = get_file_status(st.session_state.current_file_id)
            
            if file_status["status"] == "processed":
                progress_bar.progress(100)
                status_text.text("✅ Processing complete!")
                st.rerun()
                break
            elif file_status["status"] == "failed":
                st.error(f"❌ Processing failed: {file_status.get('error', 'Unknown error')}")
                break
            else:
                progress_bar.progress(min(90, (i + 1) * 3))
                status_text.text(f"Processing... ({file_status['status']})")
                time.sleep(1)
    
    elif file_status["status"] == "failed":
        st.error(f"❌ {st.session_state.current_filename} processing failed: {file_status.get('error', 'Unknown error')}")
    
    else:
        st.warning(f"⏳ {st.session_state.current_filename} status: {file_status['status']}")

else:
    # Welcome screen
    st.markdown("""
    ## Welcome to Document Chat! 🎉
    
    **How to get started:**
    1. 📤 Upload a PDF or text file using the sidebar
    2. ⏳ Wait for the document to be processed
    3. 💬 Start chatting with your document!
    
    **Features:**
    - 📄 Support for PDF and text files
    - 🧠 AI-powered document understanding
    - 🔍 Knowledge graph integration
    - 📚 Source citations for answers
    - 💾 Chat history per document
    """)
    
    # Quick demo
    st.subheader("🚀 Quick Demo")
    if st.button("Try with sample text", type="secondary"):
        # Create a sample text file
        sample_text = """
        This is a sample document about artificial intelligence.
        
        Artificial Intelligence (AI) is a branch of computer science that aims to create 
        machines capable of intelligent behavior. Machine Learning is a subset of AI that 
        focuses on algorithms that can learn from data.
        
        Key AI researchers include Geoffrey Hinton, Yann LeCun, and Andrew Ng.
        Popular AI frameworks include TensorFlow, PyTorch, and Scikit-learn.
        """
        
        # Save sample file
        with open("sample_demo.txt", "w") as f:
            f.write(sample_text)
        
        # Upload it
        with open("sample_demo.txt", "rb") as f:
            files = {"file": ("sample_demo.txt", f.read(), "text/plain")}
            headers = {"user-id": USER_ID}
            
            response = requests.post(
                f"{API_BASE_URL}/upload",
                files=files,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.current_file_id = result["file_id"]
                st.session_state.current_filename = result["filename"]
                st.success("✅ Sample document uploaded! Processing...")
                st.rerun()
            else:
                st.error("Failed to upload sample document")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Ask specific questions about your document for the best results!")
