from typing import Dict

# Tool specification
TOOL_SPEC = {
    "name": "get_weather",
    "description": "Get the current weather in a given location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, CA"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "The unit of temperature, either 'celsius' or 'fahrenheit'"
            }
        },
        "required": ["location"]
    }
}

def get_weather(location: str, unit: str = "fahrenheit") -> Dict:
    """
    Get weather information for a location
    
    Args:
        location (str): City and state (e.g., "San Francisco, CA")
        unit (str): Temperature unit (celsius or fahrenheit)
        
    Returns:
        Dict: Weather information or error message
    """
    try:
        # This is a mock implementation
        # In production, you would integrate with a real weather API
        temp = 72 if unit == "fahrenheit" else 22
        return {
            "temperature": temp,
            "unit": unit,
            "condition": "sunny",
            "humidity": 45,
            "location": location,
            "note": "This is mock data for demonstration"
        }
    except Exception as e:
        return {"error": str(e)}
