"""Super simple RAG test without complex LangChain imports."""
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_basic_rag():
    """Test basic RAG functionality."""
    print("🧪 Testing Basic RAG Pipeline\n")
    
    try:
        # Set up OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # 1. Read document
        print("1️⃣ Reading document...")
        with open("test-document.txt", "r", encoding="utf-8") as f:
            text = f.read()
        print(f"📄 Document length: {len(text)} characters")
        print(f"Content preview: {text[:100]}...\n")
        
        # 2. Simple chunking
        print("2️⃣ Creating chunks...")
        words = text.split()
        chunk_size = 50
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            chunks.append(chunk)
        print(f"✅ Created {len(chunks)} chunks\n")
        
        # 3. Test embedding (simple version)
        print("3️⃣ Testing OpenAI connection...")
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input="This is a test sentence."
        )
        embedding = response.data[0].embedding
        print(f"✅ Embedding created: {len(embedding)} dimensions\n")
        
        # 4. Test chat completion
        print("4️⃣ Testing chat completion...")
        query = "What is artificial intelligence?"
        
        # Create context from chunks
        context = "\n".join(chunks[:3])  # Use first 3 chunks as context
        
        prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0
        )
        
        answer = response.choices[0].message.content
        print(f"❓ Question: {query}")
        print(f"🤖 Answer: {answer}\n")
        
        print("🎉 Basic RAG Test Complete!")
        print("✅ Document reading: Working")
        print("✅ Text chunking: Working") 
        print("✅ OpenAI embeddings: Working")
        print("✅ OpenAI chat: Working")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your OpenAI API key is set in .env file")

if __name__ == "__main__":
    test_basic_rag()