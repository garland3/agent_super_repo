from tools.python_executor import python_executor
from code_database import code_database

def test_execution_and_storage():
    # Test code to execute
    test_code = """
print('Hello, testing code execution and database storage!')
x = 5 + 5
print(f'The result of 5 + 5 is {x}')
"""
    
    # Execute the code
    print("Executing test code...")
    result = python_executor(code=test_code, filename="test_script.py")
    
    if "error" in result:
        print(f"Execution failed: {result['error']}")
        return
        
    print(f"Execution result: {result['result']}")
    
    # Search the database for our test code
    print("\nSearching database for stored code...")
    search_result = code_database(action="search", query="Hello, testing code execution")
    
    if "error" in search_result:
        print(f"Database search failed: {search_result['error']}")
        return
        
    print(f"Found {search_result['result']['count']} matching entries in database")
    for entry in search_result['result']['results']:
        print(f"\nEntry ID: {entry['id']}")
        print(f"Short summary: {entry['short_summary']}")
        print(f"Rating: {entry['rating_0_to_5']}")
        print(f"Code:\n{entry['code']}")

if __name__ == "__main__":
    test_execution_and_storage()
