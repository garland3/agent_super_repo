from typing import List, Dict

# Tool specification
TOOL_SPEC = {
    "name": "calculate",
    "description": "Perform mathematical calculations",
    "input_schema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "description": "The mathematical operation to perform (add, subtract, multiply, divide)",
                "enum": ["add", "subtract", "multiply", "divide"]
            },
            "numbers": {
                "type": "array",
                "items": {"type": "number"},
                "description": "List of numbers to perform the operation on",
                "minItems": 2
            }
        },
        "required": ["operation", "numbers"]
    }
}

def calculate(operation: str, numbers: List[float]) -> Dict:
    """
    Perform mathematical calculations
    
    Args:
        operation (str): Operation to perform (add, subtract, multiply, divide)
        numbers (List[float]): Numbers to operate on
        
    Returns:
        Dict: Result of calculation or error message
    """
    try:
        if operation == "add":
            result = sum(numbers)
        elif operation == "subtract":
            result = numbers[0] - sum(numbers[1:])
        elif operation == "multiply":
            result = 1
            for num in numbers:
                result *= num
        elif operation == "divide":
            result = numbers[0]
            for num in numbers[1:]:
                if num == 0:
                    return {"error": "Division by zero"}
                result /= num
        else:
            return {"error": f"Unknown operation: {operation}"}
            
        return {"result": result}
        
    except Exception as e:
        return {"error": str(e)}
