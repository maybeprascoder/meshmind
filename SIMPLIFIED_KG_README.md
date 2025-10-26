# Simplified Knowledge Graph Approach

This document explains the simplified knowledge graph approach implemented in the RAG (Retrieval Augmented Generation) system.

## Overview

We've implemented a simplified hybrid retrieval system that combines:
1. **Entity-Based Retrieval**: Using entities extracted from the query
2. **Traditional Keyword Search**: Using direct text matching

This approach provides more context-aware retrieval without the complexity of graph traversal.

## How It Works

### 1. Knowledge Graph Creation

When a PDF is uploaded and processed:

1. **Text Extraction**: The system extracts text from the PDF
2. **Entity Extraction**: OpenAI is used to identify key entities (people, organizations, concepts, etc.)
3. **Relationship Extraction**: The system identifies relationships between entities
4. **Graph Construction**: Entities and relationships are stored in Neo4j

### 2. Simplified Hybrid Retrieval

When a query is received:

1. **Entity Extraction**: The system extracts key entities from the query using LLM
2. **Direct Entity Search**: It searches for chunks containing these entities
3. **Keyword Search**: In parallel, it performs traditional keyword search
4. **Result Combination**: Results from both approaches are combined
5. **Answer Generation**: The LLM generates an answer using the combined context

### 3. Benefits

- **Simpler Implementation**: No complex graph traversal required
- **Entity-Centric Retrieval**: Still focuses on key entities in the document
- **Reduced Complexity**: Easier to understand and maintain
- **Explainable Results**: Sources show whether they came from entity search or keyword search

## API Endpoints

- **POST `/upload`**: Upload a PDF file
- **GET `/file/{file_id}/status`**: Check processing status
- **POST `/query`**: Query the system with hybrid retrieval
  - Set `use_kg: true` to enable entity-based retrieval
  - Set `use_kg: false` to use only vector/keyword search
- **GET `/graph/{file_id}`**: Get knowledge graph data for visualization
- **GET `/chat-history/{file_id}`**: Get chat history for a file

## Example Query

```json
POST /query
{
  "query": "What is the relationship between AI and Machine Learning?",
  "file_id": "your-file-id",
  "session_id": "session-1",
  "use_kg": true
}
```

## Future Improvements

1. **Better Entity Matching**: Improve entity extraction from queries
2. **Entity Expansion**: Include related entities from the knowledge graph
3. **Relationship-Aware Retrieval**: Use relationships to find more relevant chunks
4. **Cross-Document Knowledge Graphs**: Connect entities across multiple documents
