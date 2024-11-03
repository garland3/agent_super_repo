# NOTE:  THIS IS A SPECIFICATINONS FILE FOR HOW TO CREATE TOOLS

# Adding New Tools

This document outlines the template and requirements for adding new tools to the system.

## Tool Structure

Each tool should be implemented as a separate Python file in the `tools` directory with the following structure:

```python
from typing import Dict, Any  # Import required types

# Tool Specification
TOOL_SPEC = {
    "name": "tool_name",
    "description": "Clear description of what the tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",  # or number, array, object, etc.
                "description": "Description of parameter 1",
                # Optional: include enum if parameter has specific allowed values
                "enum": ["value1", "value2"]  
            },
            "param2": {
                "type": "number",
                "description": "Description of parameter 2"
            }
            # Add more parameters as needed
        },
        "required": ["param1"]  # List required parameters
    }
}

def tool_name(param1: str, param2: int = default_value) -> Dict:
    """
    Main function implementing the tool's functionality
    
    Args:
        param1 (type): Description of first parameter
        param2 (type): Description of second parameter
        
    Returns:
        Dict: Result dictionary containing either:
            - Success case: Relevant output data
            - Error case: {"error": "error message"}
    """
    try:
        # Tool implementation
        result = do_something(param1, param2)
        return {"result": result}
        
    except Exception as e:
        return {"error": str(e)}
```

## Requirements

1. **File Location**: Place the tool in the `tools` directory with a descriptive filename
2. **Type Hints**: Use Python type hints for all function parameters and return values
3. **Documentation**: Include docstrings explaining:
   - What the tool does
   - Parameter descriptions
   - Return value format
4. **Error Handling**: Implement try/catch blocks and return errors in standardized format
5. **Tool Specification**: Define TOOL_SPEC with:
   - Unique tool name
   - Clear description
   - Input schema defining all parameters
   - Required parameters list

## Input Schema

The input_schema should follow JSON Schema format and include:
- `type`: Data type (string, number, array, object)
- `description`: Clear explanation of the parameter
- `enum`: (Optional) List of allowed values
- Additional validations as needed (minLength, maxItems, etc.)

## Return Format

Tools should return a dictionary with either:
- Success: `{"result": <result_data>}`
- Error: `{"error": "error message"}`

## Examples

See existing tools for reference implementations:
- calculator.py: Example of numerical operations with multiple parameters
- weather.py: Example of optional parameters and mock API implementation
- stl_viewer.py: Example of file handling and browser integration for viewing 3D models

## Testing

Add tests for new tools in test_tools.py covering:
- Normal operation
- Edge cases
- Error conditions


# NOTE:  THIS IS A SPECIFICATINONS FILE FOR HOW TO CREATE TOOLS -- DO NOT MODIFY THIS FILE
```