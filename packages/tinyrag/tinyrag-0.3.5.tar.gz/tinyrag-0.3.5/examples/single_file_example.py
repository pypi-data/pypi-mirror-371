"""
Example demonstrating TinyRag's ability to process both single code files and directories
"""

from tinyrag import TinyRag
import tempfile
import os

def create_sample_files():
    """Create sample code files for demonstration"""
    temp_dir = tempfile.mkdtemp()
    
    # Create a Python file
    python_code = '''
def calculate_fibonacci(n):
    """Calculate fibonacci number at position n"""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class MathUtils:
    """Utility class for mathematical operations"""
    
    @staticmethod
    def is_prime(num):
        """Check if a number is prime"""
        if num < 2:
            return False
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                return False
        return True
'''
    
    # Create a JavaScript file
    js_code = '''
function reverseString(str) {
    // Reverse a string using built-in methods
    return str.split('').reverse().join('');
}

const isPalindrome = (text) => {
    const cleaned = text.toLowerCase().replace(/[^a-z0-9]/g, '');
    return cleaned === cleaned.split('').reverse().join('');
};

class StringProcessor {
    constructor() {
        this.processed = [];
    }
    
    addString(str) {
        this.processed.push(str.trim());
    }
}
'''
    
    # Write files
    python_file = os.path.join(temp_dir, "math_utils.py")
    js_file = os.path.join(temp_dir, "string_utils.js")
    
    with open(python_file, "w") as f:
        f.write(python_code)
    
    with open(js_file, "w") as f:
        f.write(js_code)
    
    return temp_dir, python_file, js_file

def main():
    print("=== TinyRag Single File & Directory Processing Example ===\n")
    
    # Create sample files
    temp_dir, python_file, js_file = create_sample_files()
    print(f"Created sample files in: {temp_dir}")
    print(f"Python file: {python_file}")
    print(f"JavaScript file: {js_file}")
    
    # Initialize TinyRag
    rag = TinyRag(vector_store="memory")
    
    # Test 1: Process a single Python file
    print("\n=== Test 1: Processing Single Python File ===")
    rag.add_codebase(python_file)
    print(f"Functions in vector store after Python file: {rag.get_chunk_count()}")
    
    # Test 2: Process a single JavaScript file
    print("\n=== Test 2: Processing Single JavaScript File ===")
    rag.add_codebase(js_file)
    print(f"Functions in vector store after JS file: {rag.get_chunk_count()}")
    
    # Test 3: Search for specific functions
    print("\n=== Test 3: Searching for Functions ===")
    
    # Search for math-related functions
    math_results = rag.search_code("fibonacci mathematics prime number", k=3)
    print("Math-related functions:")
    for i, (code, score) in enumerate(math_results, 1):
        lines = code.split('\n')
        func_name = lines[3].replace('Name: ', '')
        language = lines[1].replace('Language: ', '')
        print(f"  {i}. {func_name} ({language}) - Score: {score:.3f}")
    
    # Search for string operations
    string_results = rag.search_code("string reverse palindrome text", k=3)
    print("\nString-related functions:")
    for i, (code, score) in enumerate(string_results, 1):
        lines = code.split('\n')
        func_name = lines[3].replace('Name: ', '')
        language = lines[1].replace('Language: ', '')
        print(f"  {i}. {func_name} ({language}) - Score: {score:.3f}")
    
    # Clear and test directory processing
    print("\n=== Test 4: Processing Entire Directory ===")
    rag.clear_documents()
    print("Cleared vector store")
    
    # Process the entire directory
    rag.add_codebase(temp_dir, recursive=True)
    print(f"Functions in vector store after directory processing: {rag.get_chunk_count()}")
    
    # Search for all functions
    print("\n=== Test 5: All Available Functions ===")
    all_results = rag.search_code("function method class", k=10)
    print("All functions found:")
    for i, (code, score) in enumerate(all_results, 1):
        lines = code.split('\n')
        func_name = lines[3].replace('Name: ', '')
        func_type = lines[2].replace('Type: ', '')
        language = lines[1].replace('Language: ', '')
        file_name = os.path.basename(lines[0].replace('File: ', ''))
        print(f"  {i}. {func_name} [{func_type}] ({language}) in {file_name}")
    
    # Test error handling
    print("\n=== Test 6: Error Handling ===")
    
    # Try non-existent file
    print("Testing non-existent file:")
    rag.add_codebase("non_existent_file.py")
    
    # Try unsupported file type
    print("Testing unsupported file type:")
    text_file = os.path.join(temp_dir, "readme.txt")
    with open(text_file, "w") as f:
        f.write("This is a text file, not code.")
    rag.add_codebase(text_file)
    
    # Try empty directory
    print("Testing empty directory:")
    empty_dir = os.path.join(temp_dir, "empty")
    os.makedirs(empty_dir)
    rag.add_codebase(empty_dir)
    
    print("\n=== Example Complete ===")
    print(f"Total functions in vector store: {rag.get_chunk_count()}")
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)
    print("Cleaned up temporary files")

if __name__ == "__main__":
    main()