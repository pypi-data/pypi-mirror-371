from tinyrag import Provider, TinyRag

# Example 1: Basic usage without LLM (no API key needed)
rag = TinyRag()  # Uses default all-MiniLM-L6-v2 embeddings

# Add multiple documents with multithreading
rag.add_documents([
    "path/to/doc1.pdf",
    "path/to/doc2.txt", 
    "Raw text content here"
])

# Query without LLM
results = rag.query("What is this about?")
print("Similar chunks:", results)

# Example 2: With LLM for chat functionality
provider = Provider(
    api_key="sk-xxxxxx",
    model="gpt-4",
    embedding_model="default",
    base_url="https://api.openai.com/v1"
)

rag_with_llm = TinyRag(provider=provider, vector_store="faiss", max_workers=4)

rag_with_llm.add_documents([
    "path/to/docs_or_raw_text",
    "Another document",
    "More content"
])

response = rag_with_llm.chat("Summarize the documents.")
print(response)