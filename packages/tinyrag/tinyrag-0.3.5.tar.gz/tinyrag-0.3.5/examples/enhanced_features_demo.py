#!/usr/bin/env python3
\"\"\"
TinyRag Enhanced Features Demo
Demonstrates multi-provider embedding support and intelligent document caching
\"\"\"

from tinyrag import TinyRag, Provider
import os
from typing import List


def demo_local_embeddings():
    \"\"\"Demo 1: Local embedding models (no API key required)\"\"\"
    print(\"\u2728 DEMO 1: Local Embedding Models\")
    print(\"=\" * 50)
    
    # Different local embedding models
    models = [
        \"all-MiniLM-L6-v2\",           # Default, fast and efficient
        \"all-mpnet-base-v2\",          # Higher quality, slower
        \"paraphrase-MiniLM-L6-v2\",    # Good for paraphrases
        # \"sentence-transformers/multi-qa-MiniLM-L6-cos-v1\",  # Good for Q&A
    ]
    
    for model_name in models[:2]:  # Test first 2 models
        print(f\"\n\ud83e\udde0 Testing local model: {model_name}\")
        
        try:
            # Create provider with specific local model
            provider = Provider.create_local_provider(model_name)
            
            # Create TinyRag instance
            rag = TinyRag(
                provider=provider,
                vector_store=\"memory\",
                enable_cache=True  # Enable caching
            )
            
            # Add sample documents
            docs = [
                \"Machine learning is a subset of artificial intelligence.\",
                \"Natural language processing helps computers understand human language.\",
                \"Deep learning uses neural networks with multiple layers.\"
            ]
            
            rag.add_documents(docs)
            
            # Test search
            results = rag.query(\"What is AI?\", k=2)
            print(f\"Search results for '{model_name}':\")
            for text, score in results:
                print(f\"  Score: {score:.3f} - {text[:60]}...\")
                
        except Exception as e:
            print(f\"  \u274c Error with {model_name}: {e}\")


def demo_openai_embeddings():
    \"\"\"Demo 2: OpenAI embeddings (requires API key)\"\"\"
    print(\"\n\u2728 DEMO 2: OpenAI Embeddings\")
    print(\"=\" * 50)
    
    api_key = os.getenv(\"OPENAI_API_KEY\")
    
    if not api_key:
        print(\"\ud83d\udea8 Skipping OpenAI demo - no API key found\")
        print(\"Set OPENAI_API_KEY environment variable to test OpenAI embeddings\")
        return
    
    try:
        # Create OpenAI provider
        provider = Provider.create_openai_provider(
            api_key=api_key,
            embedding_model=\"text-embedding-ada-002\"
        )
        
        rag = TinyRag(
            provider=provider,
            vector_store=\"faiss\",  # Better for larger datasets
            enable_cache=True
        )
        
        # Add documents
        docs = [
            \"OpenAI provides powerful language models through their API.\",
            \"GPT models excel at natural language understanding and generation.\",
            \"Embedding models convert text into numerical representations.\"
        ]
        
        rag.add_documents(docs)
        
        # Test search
        results = rag.query(\"What are language models?\", k=2)
        print(\"OpenAI embedding results:\")
        for text, score in results:
            print(f\"  Score: {score:.3f} - {text[:60]}...\")
            
        # Test chat if API key available
        try:
            response = rag.chat(\"Explain what embedding models do\")
            print(f\"\n\ud83e\udd16 Chat response: {response[:100]}...\")
        except Exception as e:
            print(f\"Chat failed: {e}\")
            
    except Exception as e:
        print(f\"\u274c OpenAI demo failed: {e}\")


def demo_ollama_embeddings():
    \"\"\"Demo 3: Ollama local embeddings (requires Ollama running)\"\"\"
    print(\"\n\u2728 DEMO 3: Ollama Local Embeddings\")
    print(\"=\" * 50)
    
    try:
        # Create Ollama provider
        provider = Provider.create_ollama_provider(
            embedding_model=\"nomic-embed-text\",  # Popular Ollama embedding model
            ollama_url=\"http://localhost:11434\"
        )
        
        rag = TinyRag(
            provider=provider,
            vector_store=\"memory\",
            enable_cache=True
        )
        
        # Test with small document first
        test_docs = [
            \"Ollama runs large language models locally.\",
            \"Local models provide privacy and control over your data.\"
        ]
        
        rag.add_documents(test_docs)
        
        results = rag.query(\"local AI models\", k=2)
        print(\"Ollama embedding results:\")
        for text, score in results:
            print(f\"  Score: {score:.3f} - {text[:60]}...\")
            
    except Exception as e:
        print(f\"\u274c Ollama demo failed: {e}\")
        print(\"Make sure Ollama is running: ollama serve\")
        print(\"And the embedding model is available: ollama pull nomic-embed-text\")


def demo_custom_embeddings():
    \"\"\"Demo 4: Custom embedding function\"\"\"
    print(\"\n\u2728 DEMO 4: Custom Embedding Function\")
    print(\"=\" * 50)
    
    def simple_embedding_function(texts: List[str]) -> List[List[float]]:
        \"\"\"A simple custom embedding function using TF-IDF\"\"\"
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        
        # Fit and transform texts
        embeddings = vectorizer.fit_transform(texts).toarray()
        
        return embeddings.tolist()
    
    try:
        # Create custom provider
        provider = Provider.create_custom_provider(
            embedding_function=simple_embedding_function,
            dimension=100  # TF-IDF dimension
        )
        
        rag = TinyRag(
            provider=provider,
            vector_store=\"memory\",
            enable_cache=True
        )
        
        # Add documents
        docs = [
            \"Custom embedding functions allow you to use any embedding method.\",
            \"TF-IDF is a simple but effective text representation technique.\",
            \"You can integrate your own embedding models easily.\"
        ]
        
        rag.add_documents(docs)
        
        results = rag.query(\"embedding methods\", k=2)
        print(\"Custom embedding results:\")
        for text, score in results:
            print(f\"  Score: {score:.3f} - {text[:60]}...\")
            
    except ImportError:
        print(\"\u274c Scikit-learn required for this demo: pip install scikit-learn\")
    except Exception as e:
        print(f\"\u274c Custom embedding demo failed: {e}\")


def demo_caching_benefits():
    \"\"\"Demo 5: Document caching benefits\"\"\"
    print(\"\n\u2728 DEMO 5: Document Caching Benefits\")
    print(\"=\" * 50)
    
    # Create sample documents
    sample_docs = [
        \"Document caching prevents re-processing of the same files.\",
        \"TinyRag automatically detects file changes and re-processes when needed.\",
        \"Cache improves performance significantly for repeated operations.\",
        \"Different embedding configurations use separate cache entries.\"
    ]
    
    print(\"\ud83d\udd04 First processing (no cache):\")
    
    # First time - no cache
    rag1 = TinyRag(
        provider=Provider.create_local_provider(\"all-MiniLM-L6-v2\"),
        enable_cache=True,
        cache_dir=\".demo_cache\"
    )
    
    import time
    start = time.time()
    rag1.add_documents(sample_docs)
    first_time = time.time() - start
    
    print(f\"\n\ud83d\udce6 Second processing (with cache):\")
    
    # Second time - should use cache
    rag2 = TinyRag(
        provider=Provider.create_local_provider(\"all-MiniLM-L6-v2\"),
        enable_cache=True,
        cache_dir=\".demo_cache\"
    )
    
    start = time.time()
    rag2.add_documents(sample_docs)  # Same documents
    second_time = time.time() - start
    
    print(f\"\n\u23f1\ufe0f Performance comparison:\")
    print(f\"  First run:  {first_time:.3f} seconds\")
    print(f\"  Second run: {second_time:.3f} seconds\")
    print(f\"  Speedup:    {first_time/second_time:.1f}x faster\")
    
    # Show cache info
    cache_info = rag2.get_cache_info()
    print(f\"\n\ud83d\udce6 Cache information:\")
    print(f\"  Cached documents: {cache_info['total_documents']}\")
    print(f\"  Cache size: {cache_info['cache_size_mb']:.2f} MB\")
    print(f\"  Cache directory: {cache_info['cache_directory']}\")


def demo_provider_switching():
    \"\"\"Demo 6: Switching between providers\"\"\"
    print(\"\n\u2728 DEMO 6: Provider Switching\")
    print(\"=\" * 50)
    
    docs = [\"This is a test document for provider comparison.\"]
    
    # Different providers
    providers = {
        \"Local (fast)\": Provider.create_local_provider(\"all-MiniLM-L6-v2\"),
        \"Local (quality)\": Provider.create_local_provider(\"all-mpnet-base-v2\"),
    }
    
    # Add OpenAI if API key available
    api_key = os.getenv(\"OPENAI_API_KEY\")
    if api_key:
        providers[\"OpenAI\"] = Provider.create_openai_provider(api_key)
    
    query = \"test document\"
    
    print(f\"Comparing providers for query: '{query}'\")
    print()
    
    for name, provider in providers.items():
        try:
            rag = TinyRag(
                provider=provider,
                vector_store=\"memory\",
                enable_cache=True,
                cache_dir=f\".cache_{name.lower().replace(' ', '_')}\"
            )
            
            rag.add_documents(docs)
            
            # Get provider info
            provider_info = rag.get_provider_info()
            
            results = rag.query(query, k=1)
            score = results[0][1] if results else 0.0
            
            print(f\"\ud83e\udd16 {name}:\")
            print(f\"  Model: {provider_info['embedding_model']}\")
            print(f\"  Dimension: {provider_info['embedding_dimension']}\")
            print(f\"  Score: {score:.3f}\")
            print()
            
        except Exception as e:
            print(f\"\u274c {name} failed: {e}\")
            print()


def main():
    \"\"\"Run all demos\"\"\"
    print(\"\ud83c\udf86 TinyRag Enhanced Features Demo\")
    print(\"=\" * 60)
    
    # Run demos
    demo_local_embeddings()
    demo_openai_embeddings()
    demo_ollama_embeddings()
    demo_custom_embeddings()
    demo_caching_benefits()
    demo_provider_switching()
    
    print(\"\n\u2728 Demo complete! \")
    print(\"\n\ud83d\udca1 Key Features Demonstrated:\")
    print(\"  \u2705 Multiple embedding providers (local, OpenAI, Ollama, custom)\")
    print(\"  \u2705 Intelligent document caching\")
    print(\"  \u2705 Performance improvements through caching\")
    print(\"  \u2705 Easy provider switching\")
    print(\"  \u2705 Cache management and information\")


if __name__ == \"__main__\":
    main()
