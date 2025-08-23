"""
Example: Custom System Prompts in TinyRag
This example shows how to set and use custom system prompts for different use cases.
"""

from tinyrag import Provider, TinyRag

def main():
    print("=== TinyRag Custom System Prompt Examples ===\n")
    
    # Initialize provider with API key
    provider = Provider(
        api_key="sk-xxxxxx",  # Replace with your API key
        model="gpt-4",
        embedding_model="default",
        base_url="https://api.openai.com/v1"
    )
    
    # Example 1: Default System Prompt
    print("1. Using Default System Prompt")
    rag_default = TinyRag(provider=provider, vector_store="memory")
    
    # Add some sample documents
    rag_default.add_documents([
        "TinyRag is a Python library for Retrieval-Augmented Generation.",
        "It supports multiple document formats including PDF and DOCX.",
        "The library uses vector stores for efficient similarity search."
    ])
    
    print(f"Default prompt: {rag_default.get_system_prompt()}")
    response = rag_default.chat("What is TinyRag?")
    print(f"Response: {response}\n")
    
    # Example 2: Technical Documentation Assistant
    print("2. Technical Documentation Assistant")
    tech_prompt = """You are a technical documentation assistant. 
    Provide clear, concise explanations with examples where helpful. 
    Focus on practical implementation details and best practices. 
    Use the provided context to give accurate technical information."""
    
    rag_tech = TinyRag(
        provider=provider, 
        vector_store="memory",
        system_prompt=tech_prompt
    )
    
    # Add technical documentation
    rag_tech.add_documents([
        "API endpoints support GET, POST, PUT, and DELETE methods.",
        "Authentication requires Bearer token in the Authorization header.",
        "Rate limiting is 1000 requests per hour per API key."
    ])
    
    response = rag_tech.chat("How do I authenticate API requests?")
    print(f"Tech Assistant Response: {response}\n")
    
    # Example 3: Code Review Assistant
    print("3. Code Review Assistant")
    code_prompt = """You are an expert code reviewer. 
    Analyze the provided code context and give constructive feedback. 
    Focus on code quality, security issues, performance optimizations, and best practices. 
    Provide specific suggestions for improvement."""
    
    rag_code = TinyRag(provider=provider, vector_store="memory")
    rag_code.set_system_prompt(code_prompt)  # Set prompt after initialization
    
    # Add code snippets
    rag_code.add_documents([
        "def authenticate_user(username, password): return username == 'admin' and password == '123'",
        "SELECT * FROM users WHERE id = '" + str(user_id) + "'",
        "for i in range(len(items)): process_item(items[i])"
    ])
    
    response = rag_code.chat("Review this authentication code for security issues")
    print(f"Code Reviewer Response: {response}\n")
    
    # Example 4: Customer Support Agent
    print("4. Customer Support Agent")
    support_prompt = """You are a friendly and helpful customer support agent.
    Always be polite, empathetic, and solution-focused.
    Use the provided context to help resolve customer issues.
    If you cannot find a solution in the context, apologize and suggest contacting technical support."""
    
    rag_support = TinyRag(provider=provider, vector_store="memory")
    rag_support.set_system_prompt(support_prompt)
    
    # Add support documentation
    rag_support.add_documents([
        "To reset your password, click 'Forgot Password' on the login page.",
        "Refunds are processed within 5-7 business days.",
        "For technical issues, contact support@example.com or call 1-800-HELP."
    ])
    
    response = rag_support.chat("I can't log into my account")
    print(f"Support Agent Response: {response}\n")
    
    # Example 5: Educational Tutor
    print("5. Educational Tutor")
    tutor_prompt = """You are a patient and encouraging educational tutor.
    Explain concepts clearly and break down complex topics into simple steps.
    Provide examples and analogies to help students understand.
    Always encourage learning and ask follow-up questions to check understanding."""
    
    rag_tutor = TinyRag(
        provider=provider, 
        vector_store="memory",
        system_prompt=tutor_prompt
    )
    
    # Add educational content
    rag_tutor.add_documents([
        "Machine learning is like teaching a computer to recognize patterns.",
        "Supervised learning uses labeled examples to train models.",
        "Neural networks are inspired by how the human brain processes information."
    ])
    
    response = rag_tutor.chat("What is machine learning?")
    print(f"Tutor Response: {response}\n")
    
    # Example 6: Domain-Specific Expert (Medical)
    print("6. Medical Information Assistant")
    medical_prompt = """You are a medical information assistant.
    Provide accurate medical information based on the provided context.
    Always include disclaimers that this is for informational purposes only.
    Recommend consulting healthcare professionals for medical advice.
    Be precise and use appropriate medical terminology while remaining accessible."""
    
    rag_medical = TinyRag(provider=provider, vector_store="memory")
    rag_medical.set_system_prompt(medical_prompt)
    
    # Add medical information
    rag_medical.add_documents([
        "Hypertension is defined as blood pressure consistently above 140/90 mmHg.",
        "Regular exercise can help reduce blood pressure by 4-9 mmHg.",
        "The DASH diet emphasizes fruits, vegetables, and low-fat dairy products."
    ])
    
    response = rag_medical.chat("What is hypertension?")
    print(f"Medical Assistant Response: {response}\n")
    
    # Example 7: Creative Writing Assistant
    print("7. Creative Writing Assistant")
    creative_prompt = """You are a creative writing assistant.
    Help writers brainstorm ideas, develop characters, and improve their storytelling.
    Be imaginative and inspiring in your responses.
    Use the provided context to enhance creative projects and offer constructive feedback."""
    
    rag_creative = TinyRag(
        provider=provider,
        vector_store="memory", 
        system_prompt=creative_prompt
    )
    
    # Add creative writing resources
    rag_creative.add_documents([
        "Character development requires understanding motivations, flaws, and growth arcs.",
        "Show don't tell: Use actions and dialogue to reveal character traits.",
        "Plot structure follows setup, confrontation, and resolution patterns."
    ])
    
    response = rag_creative.chat("How do I create compelling characters?")
    print(f"Creative Assistant Response: {response}\n")
    
    print("=== Custom System Prompt Examples Complete ===")

if __name__ == "__main__":
    main()