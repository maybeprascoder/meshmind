# MeshMind RAG - Python Version 🐍

A complete Python rewrite of the RAG (Retrieval Augmented Generation) system using modern AI libraries.

## 🚀 Features

- **FastAPI** - Modern, fast web framework
- **LangChain** - AI/ML library for RAG
- **FAISS** - Vector similarity search
- **MongoDB** - Document storage
- **Neo4j** - Knowledge graph
- **Redis** - Caching and job queue
- **OpenAI** - Embeddings and LLM

## 📁 Project Structure

```
python-rag/
├── main.py                 # Main application
├── requirements.txt        # Dependencies
├── .env                   # Environment variables
├── config/
│   ├── settings.py        # Configuration
│   └── database.py        # Database connections
├── models/
│   ├── chunk.py          # Chunk model
│   ├── file.py           # File model
│   └── job.py            # Job model
├── services/
│   ├── ingest.py         # File ingestion
│   ├── search.py         # Search & retrieval
│   ├── chat.py           # Chat & Q&A
│   └── worker.py         # Background processing
├── api/
│   ├── ingest_api.py     # Ingest endpoints
│   └── query_api.py      # Query endpoints
└── tests/
    └── test_rag.py       # RAG tests
```

## 🛠️ Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the application:**
   ```bash
   # Ingest API (Port 8081)
   python main.py ingest
   
   # Query API (Port 8082)
   python main.py query
   
   # Background Worker
   python main.py worker
   ```

## 🧪 Testing

```bash
# Run tests
python tests/test_rag.py

# Or with pytest
pytest tests/
```

## 📚 API Endpoints

### Ingest API (Port 8081)
- `POST /api/ingest/register` - Register file for processing
- `GET /api/ingest/status?job_id=...` - Get job status
- `GET /api/ingest/health` - Health check

### Query API (Port 8082)
- `POST /api/search` - Search for information
- `POST /api/chat` - Chat with documents
- `GET /api/chat/stream` - Stream chat responses
- `GET /api/health` - Health check

## 🔄 Usage Example

```python
import requests

# 1. Register a file
response = requests.post("http://localhost:8081/api/ingest/register", json={
    "file_id": "test-file",
    "filename": "test-document.txt",
    "hash": "abc123"
})
job_id = response.json()["job_id"]

# 2. Search for information
response = requests.post("http://localhost:8082/api/search", json={
    "query": "What is artificial intelligence?",
    "k": 5
})
results = response.json()

# 3. Chat with documents
response = requests.post("http://localhost:8082/api/chat", json={
    "query": "Explain machine learning",
    "session_id": "user123"
})
answer = response.json()
```

## 🎯 Key Improvements over TypeScript

- **10x simpler** - Less boilerplate code
- **Better AI libraries** - LangChain, LlamaIndex
- **Easier development** - Python ecosystem
- **Better documentation** - More examples and tutorials
- **Faster iteration** - Quick testing and debugging

## 🔧 Development

```bash
# Format code
black .
isort .

# Run linting
flake8 .

# Run tests
pytest tests/ -v
```
