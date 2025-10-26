# MeshMind RAG System

> **Enterprise-grade Retrieval-Augmented Generation (RAG) system with knowledge graphs and multi-phase architecture**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

MeshMind is a comprehensive RAG system that demonstrates enterprise-grade architecture with advanced AI integration, knowledge graph construction, and modern software engineering practices. The system showcases the evolution from simplified prototypes to production-ready microservices.

## 🏗️ Architecture Phases

### **Phase 1: Core System**
- **Monolithic**: Single FastAPI application with comprehensive functionality
- **Processing**: Synchronous document processing with immediate responses
- **Knowledge Graph**: Entity extraction and hybrid retrieval
- **Dependencies**: Optimized minimal dependencies
- **Use Case**: Rapid deployment and demonstration

### **Phase 2: Enterprise Architecture**
- **Microservices**: Separated ingest/query APIs with background workers
- **Databases**: MongoDB (chunks), Neo4j (knowledge graphs), Redis (caching)
- **Processing**: Asynchronous job queue with BullMQ/Celery
- **Scalability**: Production-ready with comprehensive error handling
- **Use Case**: High-scale production deployments

### **Phase 3: Advanced Integration**
- **MCP Protocol**: Model Context Protocol implementation
- **External APIs**: Notion and Jira integration
- **Content Processing**: External content through unified pipeline
- **Use Case**: Enterprise integrations and external data sources

## 🚀 Quick Start

### **Phase 1 (Core System)**

1. **Clone the repository**
   ```bash
   git clone https://github.com/maybeprascoder/meshmind.git
   cd MeshMind-RAG-System
   ```

2. **Install dependencies**
   ```bash
   pip install -r simple_requirements.txt
   ```

3. **Start the API server**
   ```bash
   python simple_app.py
   ```

4. **Access API documentation**
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### **Phase 2 (Enterprise Architecture)**

1. **Set up databases**
   ```bash
   # MongoDB, Neo4j, Redis required
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

3. **Start microservices**
   ```bash
   python main.py ingest    # Port 8081
   python main.py query      # Port 8082
   python main.py worker     # Background processing
   ```

## 🎨 Features

### **Core RAG Capabilities**
- ✅ **PDF Processing**: PyPDF2 integration for document extraction
- ✅ **Text Chunking**: Intelligent document segmentation
- ✅ **Vector Embeddings**: OpenAI text-embedding-3-small
- ✅ **Hybrid Search**: Vector similarity + keyword matching
- ✅ **Knowledge Graphs**: Entity extraction and relationship mapping
- ✅ **Source Citations**: Transparent answer attribution

### **Phase 1 Features**
- ✅ **Unified API**: Single endpoint for all operations
- ✅ **Immediate Processing**: Synchronous document processing
- ✅ **Mock Integration**: Self-contained system
- ✅ **Easy Deployment**: Minimal configuration required

### **Phase 2 Features**
- ✅ **Microservices**: Separated ingest/query APIs
- ✅ **Background Jobs**: Asynchronous processing pipeline
- ✅ **Database Integration**: MongoDB, Neo4j, Redis
- ✅ **Job Tracking**: Detailed progress monitoring
- ✅ **Error Handling**: Comprehensive error management
- ✅ **Scalability**: Production-ready architecture

## 📊 System Comparison

| Feature | Phase 1 (Core) | Phase 2 (Enterprise) | Phase 3 (Advanced) |
|---------|---------------|---------------------|-------------------|
| **Architecture** | Monolithic | Microservices | MCP Integration |
| **Processing** | Sync | Async (jobs) | Async (external) |
| **Storage** | Integrated | Distributed | External APIs |
| **Setup Time** | 2 minutes | 30+ minutes | 1+ hour |
| **Dependencies** | Minimal | Comprehensive | MCP protocol |
| **Scalability** | Medium | High | High |

## 🛠️ Technology Stack

### **Backend**
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and serialization
- **PyPDF2**: PDF text extraction
- **OpenAI**: GPT-4 and embeddings
- **Neo4j**: Graph database for knowledge graphs

### **Databases** (Phase 2)
- **MongoDB**: Document storage and chunking
- **Neo4j**: Knowledge graph relationships
- **Redis**: Caching and job queuing

### **AI/ML**
- **OpenAI GPT-4**: Language model integration
- **Text Embeddings**: Vector similarity search
- **Knowledge Graphs**: Entity extraction and relationships
- **Hybrid Retrieval**: Combining multiple search strategies

## 🔧 API Endpoints

### **Core Endpoints**
- `POST /upload` - Upload documents
- `GET /file/{file_id}/status` - Check processing status
- `POST /query` - Query documents with hybrid retrieval
- `GET /graph/{file_id}` - View knowledge graph
- `GET /files` - List user files
- `GET /health` - Health check

### **Enterprise Endpoints** (Phase 2)
- `POST /api/ingest/register` - Register file for processing
- `GET /api/ingest/status` - Job status tracking
- `POST /api/search` - Vector and keyword search
- `POST /api/chat` - Conversational interface

## 📈 Performance

- **Processing Speed**: 2-5 seconds per document (Phase 1), 10-30 seconds (Phase 2)
- **Chunk Size**: 1000 characters (configurable)
- **Embedding Model**: text-embedding-3-small (1536 dimensions)
- **Knowledge Graph**: 20-50 entities per document
- **Concurrent Users**: Supports multiple simultaneous uploads

## 🎯 Use Cases

### **Document Analysis**
- Research paper summarization
- Legal document review
- Technical documentation Q&A
- Resume analysis and insights

### **Knowledge Management**
- Corporate knowledge base
- Educational content processing
- Customer support automation
- Content discovery and search

### **Integration Scenarios**
- Notion workspace integration
- Jira issue analysis
- Confluence page processing
- GitHub documentation

## 🚀 Deployment

### **Phase 1 (Core System)**
```bash
python simple_app.py
```

### **Phase 2 (Enterprise)**
```bash
python main.py ingest
python main.py query
python main.py worker
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## 👨‍💻 Author

**Prasoon Kumar and Vivek Hegde**
- GitHub: [@maybeprascoder][@HEGDEVIVEK]
- LinkedIn:(https://www.linkedin.com/in/prasoon-singh-ty/)(https://www.linkedin.com/in/vivek-s-hegde-2001)

## 🙏 Acknowledgments

- OpenAI for embedding models
- GeminiAI for gemini 2.5 Flash
- FastAPI team for the excellent web framework
- Neo4j for graph database capabilities

---

**⭐ Star this repository if you found it helpful!**