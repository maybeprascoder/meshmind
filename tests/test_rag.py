"""Test RAG functionality."""
import pytest
import asyncio
from services.ingest import IngestService
from services.search import SearchService
from services.chat import ChatService


class TestRAG:
    """Test RAG pipeline."""
    
    def test_chunking(self):
        """Test text chunking."""
        from langchain.text_splitter import CharacterTextSplitter
        
        text = "This is a test document. It has multiple sentences. Each sentence should be chunked properly."
        splitter = CharacterTextSplitter(chunk_size=50, chunk_overlap=10)
        chunks = splitter.split_text(text)
        
        assert len(chunks) > 0
        assert all(len(chunk) <= 50 for chunk in chunks)
    
    def test_embeddings(self):
        """Test embedding generation."""
        from langchain.embeddings import OpenAIEmbeddings
        
        embeddings = OpenAIEmbeddings()
        text = "This is a test sentence."
        embedding = embeddings.embed_query(text)
        
        assert len(embedding) == 1536  # OpenAI text-embedding-3-small dimension
        assert all(isinstance(x, float) for x in embedding)
    
    def test_vector_search(self):
        """Test vector search."""
        from langchain.embeddings import OpenAIEmbeddings
        from langchain.vectorstores import FAISS
        from langchain.schema import Document
        
        # Create test documents
        documents = [
            Document(page_content="Artificial intelligence is a branch of computer science."),
            Document(page_content="Machine learning is a subset of artificial intelligence."),
            Document(page_content="Deep learning uses neural networks with multiple layers.")
        ]
        
        # Create vector store
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(documents, embeddings)
        
        # Test search
        query = "What is AI?"
        results = vectorstore.similarity_search(query, k=2)
        
        assert len(results) == 2
        assert all(isinstance(doc, Document) for doc in results)
    
    def test_chat_service(self):
        """Test chat service."""
        # This would require a full database setup
        # For now, just test the service can be instantiated
        chat_service = ChatService()
        assert chat_service is not None


if __name__ == "__main__":
    # Run basic tests
    test = TestRAG()
    test.test_chunking()
    test.test_embeddings()
    test.test_vector_search()
    test.test_chat_service()
    print("✅ All tests passed!")
