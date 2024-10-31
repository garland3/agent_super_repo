from utils import handle_tool_call

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

if __name__ == "__main__":
    print("Testing tools...")
    test_weather()
    test_calculator()
    test_file_search()
