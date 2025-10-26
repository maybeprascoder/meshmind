# Knowledge Graph Enhanced RAG System

This document explains how the knowledge graph enhancement works in our RAG (Retrieval Augmented Generation) system.

## Overview

We've implemented a hybrid retrieval system that combines:
1. **Vector/Keyword Search**: Traditional text-based retrieval
2. **Knowledge Graph**: Entity and relationship-based retrieval

This approach provides more context-aware and semantically rich information retrieval.

## How It Works

### 1. Knowledge Graph Creation

When a PDF is uploaded and processed:

1. **Text Extraction**: The system extracts text from the PDF
2. **Chunking**: Text is split into manageable chunks
3. **Entity Extraction**: OpenAI is used to identify key entities (people, organizations, concepts, etc.)
4. **Relationship Extraction**: The system identifies relationships between entities
5. **Graph Construction**: Entities and relationships are stored in Neo4j
6. **MongoDB Backup**: The graph is also stored in MongoDB for redundancy

### 2. Hybrid Retrieval

When a query is received:

1. **Entity Recognition**: The system extracts key entities from the query
2. **Graph Traversal**: It finds relevant entities and relationships in the knowledge graph
3. **Context Retrieval**: It retrieves text chunks associated with those entities
4. **Vector Search**: In parallel, it performs traditional keyword search
5. **Result Combination**: Results from both approaches are combined
6. **Answer Generation**: The LLM generates an answer using the combined context

### 3. Benefits

- **Better Context Understanding**: The knowledge graph captures semantic relationships
- **Entity-Centric Retrieval**: Focuses on key entities in the document
- **Reduced Hallucinations**: More accurate information retrieval
- **Explainable Results**: Sources show whether they came from graph or vector search

## API Endpoints

- **POST `/upload`**: Upload a PDF file
- **GET `/file/{file_id}/status`**: Check processing status
- **POST `/query`**: Query the system with hybrid retrieval
  - Set `use_kg: true` to enable knowledge graph retrieval
  - Set `use_kg: false` to use only vector/keyword search
- **GET `/graph/{file_id}`**: Get knowledge graph data for visualization
- **GET `/chat-history/{file_id}`**: Get chat history for a file

## Testing

Use the provided test scripts:
- `test_pdf_upload.py`: Test basic PDF processing
- `test_knowledge_graph.py`: Test knowledge graph creation and hybrid retrieval

## Example Query

```json
POST /query
{
  "query": "What is the relationship between AI and machine learning?",
  "file_id": "your-file-id",
  "session_id": "session-1",
  "use_kg": true
}
```

## Knowledge Graph Schema

### Nodes
- **Entity**: Represents a person, organization, concept, technology, etc.
  - Properties: id, name, type, mentions (page numbers)

### Relationships
- **RELATIONSHIP**: Connects two entities
  - Properties: type, context

## Future Improvements

1. **Graph Embeddings**: Add vector embeddings to graph nodes
2. **Multi-hop Reasoning**: Traverse multiple relationships for complex queries
3. **Interactive Graph Visualization**: Add a UI for exploring the knowledge graph
4. **Temporal Analysis**: Track how concepts evolve across documents
5. **Cross-Document Knowledge Graphs**: Connect entities across multiple documents
