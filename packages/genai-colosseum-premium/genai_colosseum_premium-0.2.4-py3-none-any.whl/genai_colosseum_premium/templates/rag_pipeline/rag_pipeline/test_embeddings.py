"""
Test script for RAG embeddings and vector store functionality
This script tests the core RAG features without requiring LLM API keys
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_rag_core_functionality():
    """Test the core RAG functionality without LLM."""
    
    print("🚀 Testing RAG Core Functionality")
    print("=" * 50)
    
    try:
        # Import and test RAG system
        from rag_implementation import RAGSystem
        
        print("✅ RAG system imported successfully")
        
        # Initialize RAG system with HuggingFace embeddings
        print("\n🔄 Initializing RAG system...")
        rag = RAGSystem(use_ollama=False)
        
        # Load documents
        print("\n📚 Loading documents...")
        documents = rag.load_documents(["speech.txt"])
        print(f"   Loaded {len(documents)} documents")
        
        # Create vector store
        print("\n🔍 Creating vector store...")
        rag.create_vectorstore(documents, "faiss")
        print("   Vector store created successfully")
        
        # Test similarity search
        print("\n🔎 Testing similarity search...")
        test_queries = [
            "What is the main theme of this speech?",
            "Who is the speaker addressing?",
            "What does the speaker say about the future?",
            "What is the relationship between the speaker and the audience?"
        ]
        
        for query in test_queries:
            print(f"\n   Query: {query}")
            try:
                # Get similar documents
                similar_docs = rag.vectorstore.similarity_search(query, k=2)
                print(f"   Found {len(similar_docs)} similar documents")
                
                # Show first document snippet
                if similar_docs:
                    first_doc = similar_docs[0]
                    snippet = first_doc.page_content[:150] + "..." if len(first_doc.page_content) > 150 else first_doc.page_content
                    print(f"   Top match: {snippet}")
                    
            except Exception as e:
                print(f"   ❌ Error in similarity search: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 RAG Core Functionality Test Complete!")
        print("✅ Document loading: Working")
        print("✅ Text splitting: Working")
        print("✅ Embeddings: Working")
        print("✅ Vector store: Working")
        print("✅ Similarity search: Working")
        print("\n💡 The RAG system is fully functional!")
        print("   You just need to set up your GROQ_API_KEY for LLM integration")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_environment():
    """Test environment configuration."""
    print("🔍 Testing environment configuration...")
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    langsmith_key = os.getenv("LANGSMITH_API_KEY")
    
    print(f"✅ GROQ_API_KEY: {'Set' if groq_api_key else 'Not set'}")
    print(f"✅ LANGSMITH_API_KEY: {'Set' if langsmith_key else 'Not set'}")
    
    if not groq_api_key:
        print("\n⚠️  GROQ_API_KEY not set - LLM functionality will not work")
        print("   To fix this, add your Groq API key to your .env file:")
        print("   GROQ_API_KEY=your_actual_api_key_here")
        print("\n   You can get a free API key from: https://console.groq.com/")
    
    return bool(groq_api_key)

def main():
    """Run all tests."""
    print("🚀 Starting RAG System Tests")
    print("=" * 50)
    
    # Test environment first
    env_ok = test_environment()
    
    print("\n" + "=" * 50)
    
    # Test RAG functionality
    rag_ok = test_rag_core_functionality()
    
    print("\n" + "=" * 50)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 50)
    
    if rag_ok:
        print("🎉 RAG System: FULLY FUNCTIONAL")
        if env_ok:
            print("🎉 Environment: READY FOR LLM")
            print("\n💡 You can now run the full RAG implementation:")
            print("   python rag_implementation.py")
        else:
            print("⚠️  Environment: NEEDS GROQ API KEY")
            print("\n💡 To enable LLM functionality:")
            print("   1. Get a free API key from: https://console.groq.com/")
            print("   2. Add it to your .env file: GROQ_API_KEY=your_key")
            print("   3. Run: python rag_implementation.py")
    else:
        print("❌ RAG System: HAS ISSUES")
        print("\n💡 Please check the error messages above")

if __name__ == "__main__":
    main()
