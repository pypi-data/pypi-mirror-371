"""
Demonstration of TinyRag's enhanced structured responses with citations and source tracking
"""

from tinyrag import TinyRag, Provider
import json
import time

def demo_structured_responses():
    """Demonstrate structured response features with citations"""
    
    print("🚀 TinyRag Structured Response Demo")
    print("=" * 50)
    
    # Create TinyRag instance with local embeddings (no API key needed for search)
    print("\n📦 Initializing TinyRag with local embeddings...")
    rag = TinyRag(
        vector_store="memory",
        chunk_size=400,
        enable_cache=True
    )
    
    # Add sample documents with different sources
    print("\n📄 Adding sample documents...")
    sample_docs = [
        "machine_learning.txt",  # This will be treated as raw text since file doesn't exist
        """Machine learning is a subset of artificial intelligence (AI) that focuses on algorithms 
        that can learn and make decisions from data. Common techniques include supervised learning, 
        unsupervised learning, and reinforcement learning. Popular algorithms include linear regression, 
        decision trees, neural networks, and support vector machines.""",
        
        """Deep learning is a specialized branch of machine learning that uses neural networks 
        with multiple layers. It's particularly effective for image recognition, natural language 
        processing, and speech recognition. Deep learning models require large amounts of data 
        and computational resources but can achieve remarkable accuracy.""",
        
        """Data science combines statistics, computer science, and domain expertise to extract 
        insights from data. The data science process typically includes data collection, cleaning, 
        exploration, modeling, and interpretation. Tools commonly used include Python, R, SQL, 
        and various visualization libraries."""
    ]
    
    rag.add_documents(sample_docs)
    
    # Demo 1: Basic structured search without LLM
    print("\n" + "=" * 60)
    print("📊 DEMO 1: Structured Search Results (No LLM Required)")
    print("=" * 60)
    
    query = "neural networks and deep learning"
    
    # Text format
    print(f"\n🔍 Query: '{query}'\n")
    print("📝 Text Format:")
    print("-" * 20)
    result_text = rag.query_structured(query, k=3, format_type="text")
    print(result_text)
    
    # JSON format
    print("\n📋 JSON Format:")
    print("-" * 20)
    result_json = rag.query_structured(query, k=3, format_type="json")
    print(json.dumps(result_json, indent=2))
    
    # Markdown format
    print("\n📝 Markdown Format:")
    print("-" * 20)
    result_md = rag.query_structured(query, k=3, format_type="markdown")
    print(result_md)
    
    # Demo 2: Chat with structured responses (requires API key)
    print("\n" + "=" * 60)
    print("💬 DEMO 2: Structured Chat Responses (Requires API Key)")
    print("=" * 60)
    
    # Check if we can do LLM chat
    api_key = input("\n🔑 Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if api_key:
        # Create provider with API key for chat functionality
        provider = Provider(
            api_key=api_key,
            model="gpt-3.5-turbo",
            embedding_provider="local"  # Still use local embeddings for cost efficiency
        )
        
        # Create new RAG instance with provider
        rag_with_llm = TinyRag(
            provider=provider,
            vector_store="memory",
            chunk_size=400,
            system_prompt="You are a helpful AI assistant specializing in machine learning and data science. Provide clear, accurate explanations based on the given context."
        )
        
        # Add the same documents
        rag_with_llm.add_documents(sample_docs)
        
        # Demo structured chat
        chat_query = "What is the difference between machine learning and deep learning?"
        
        print(f"\n💭 Chat Query: '{chat_query}'\n")
        
        print("📝 Text Format:")
        print("-" * 20)
        chat_result = rag_with_llm.chat_structured(chat_query, k=3, format_type="text")
        print(chat_result)
        
        print("\n📋 JSON Format:")
        print("-" * 20)
        chat_json = rag_with_llm.chat_structured(chat_query, k=3, format_type="json")
        print(json.dumps(chat_json, indent=2))
        
        print("\n📝 Markdown Format:")
        print("-" * 20)
        chat_md = rag_with_llm.chat_structured(chat_query, k=3, format_type="markdown")
        print(chat_md)
        
        # Demo comparison with old vs new chat methods
        print("\n" + "=" * 60)
        print("🔄 COMPARISON: Old vs New Chat Methods")
        print("=" * 60)
        
        comparison_query = "How does supervised learning work?"
        
        print(f"\n❓ Query: '{comparison_query}'\n")
        
        print("🔸 OLD METHOD (chat):")
        print("-" * 25)
        old_result = rag_with_llm.chat(comparison_query, k=2)
        print(old_result)
        
        print(f"\n🔹 NEW METHOD (chat_structured):")
        print("-" * 30)
        new_result = rag_with_llm.chat_structured(comparison_query, k=2, format_type="text")
        print(new_result)
        
    else:
        print("⏭️  Skipping chat demo (no API key provided)")
        print("💡 The structured search demo above works without any API keys!")
    
    # Demo 3: Working with file documents (if available)
    print("\n" + "=" * 60)
    print("📁 DEMO 3: File Source Tracking")
    print("=" * 60)
    
    print("\n💡 When you add actual files, TinyRag will track:")
    print("   • Source file names")
    print("   • Document types (pdf, docx, txt)")
    print("   • Chunk positions within documents")
    print("   • File metadata")
    print("\n🎯 Example with a real file:")
    print("   rag.add_documents(['research_paper.pdf'])")
    print("   result = rag.query_structured('methodology')")
    print("   # Will show: Source: research_paper.pdf, Page info, etc.")
    
    # Demo 4: Advanced features
    print("\n" + "=" * 60)
    print("🎛️  DEMO 4: Advanced Features")
    print("=" * 60)
    
    print("\n🔧 Available output formats:")
    formats = ["text", "json", "markdown", "structured"]
    for fmt in formats:
        result = rag.query_structured("data science tools", k=1, format_type=fmt)
        print(f"   • {fmt}: {type(result).__name__}")
    
    print("\n⚡ Performance benefits:")
    print("   • Source citations show exactly where information came from")
    print("   • Relevance scores help assess answer quality")
    print("   • Structured format enables easy integration with other systems")
    print("   • JSON output perfect for APIs and web applications")
    
    print("\n🎯 Use cases:")
    print("   • Research assistance with source tracking")
    print("   • Document Q&A with proper attribution")
    print("   • Knowledge base systems with citations")
    print("   • API responses with structured data")
    
    print("\n✅ Demo completed! TinyRag now provides:")
    print("   🔗 Source citations")
    print("   📊 Structured output formats")
    print("   🎯 Better organization")
    print("   📈 Confidence scoring")
    print("   ⚡ Performance tracking")

if __name__ == "__main__":
    try:
        demo_structured_responses()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo error: {e}")
        print("💡 Make sure you have TinyRag properly installed with: pip install tinyrag")