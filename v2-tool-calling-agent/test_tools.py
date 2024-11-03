from utils import handle_tool_call
import os

def test_weather():
    result = handle_tool_call({
        "name": "get_weather",
        "input": {"location": "Seattle, WA"}
    })
    print("Weather test result:", result)

def test_calculator():
    result = handle_tool_call({
        "name": "calculate",
        "input": {
            "operation": "add",
            "numbers": [2, 2]
        }
    })
    print("Calculator test result:", result)

def test_file_search():
    result = handle_tool_call({
        "name": "search_files",
        "input": {
            "directory": ".",
            "pattern": "*.py"
        }
    })
    print("File search test result:", result)

def test_selenium_browser():
    result = handle_tool_call({
        "name": "selenium_browser_action",
        "input": {
            "action": "screenshot",
            "url": "https://www.example.com",
            "output_dir": "test_selenium_outputs"
        }
    })
    print("Selenium browser test result:", result)

def test_python_executor():
    # Test basic code execution
    result = handle_tool_call({
        "name": "python_executor",
        "input": {
            "code": "print('Hello, World!')\nprint(2 + 2)"
        }
    })
    print("Python executor basic test result:", result)

    # Test with custom filename
    result = handle_tool_call({
        "name": "python_executor",
        "input": {
            "code": "import math\nprint(math.pi)",
            "filename": "math_test.py"
        }
    })
    print("Python executor custom filename test result:", result)

    # Test error handling
    result = handle_tool_call({
        "name": "python_executor",
        "input": {
            "code": "print(undefined_variable)"
        }
    })
    print("Python executor error test result:", result)

def test_file_writer():
    test_file = "test_output/test_file.txt"
    test_dir = os.path.dirname(test_file)
    
    # Clean up from previous tests if needed
    if os.path.exists(test_file):
        os.remove(test_file)
    if os.path.exists(test_dir):
        os.rmdir(test_dir)

    # Test basic write operation
    result = handle_tool_call({
        "name": "file_writer",
        "input": {
            "path": test_file,
            "content": "Hello, World!\n"
        }
    })
    print("File writer basic test result:", result)

    # Test append operation
    result = handle_tool_call({
        "name": "file_writer",
        "input": {
            "path": test_file,
            "content": "Second line\n",
            "append": True
        }
    })
    print("File writer append test result:", result)

    # Test error case - invalid path
    result = handle_tool_call({
        "name": "file_writer",
        "input": {
            "path": "/invalid/path/test.txt",
            "content": "This should fail"
        }
    })
    print("File writer error test result:", result)

    # Clean up test files
    if os.path.exists(test_file):
        os.remove(test_file)
    if os.path.exists(test_dir):
        os.rmdir(test_dir)

if __name__ == "__main__":
    print("Testing tools...")
    test_weather()
    test_calculator()
    test_file_search()
    test_selenium_browser()
    test_python_executor()
    test_file_writer()
