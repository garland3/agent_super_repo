# Tool Calling System with Claude

This system demonstrates tool calling capabilities using Anthropic's Claude API. It provides a framework for defining tools that Claude can use to accomplish various tasks.

## Setup

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Configure the system:
   - Copy `config/secrets.yaml` to `.secrets.yaml` and add your Anthropic API key
   - Or set the environment variable: `ANTHROPIC_API_KEY`

3. Run the system:
```bash
python main.py
```

## Available Tools

1. Weather Tool (`tools/weather.py`)
   - Get weather information for a location
   - Example: "What's the weather in San Francisco?"

2. Calculator Tool (`tools/calculator.py`)
   - Perform mathematical calculations
   - Example: "Calculate 25 divided by 5"

3. File Search Tool (`tools/file_search.py`)
   - Search for files in directories
   - Example: "Find all Python files in the current directory"

## Adding New Tools

To add a new tool:

1. Create a new Python file in the `tools` directory
2. Define the tool specification using `TOOL_SPEC` dictionary
3. Implement the tool's functionality
4. The tool will be automatically loaded by the system

Example tool structure:
```python
TOOL_SPEC = {
    "name": "tool_name",
    "description": "Tool description",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }
}

def tool_function(param1: str):
    # Tool implementation
    pass
```

## Configuration

- `config/settings.yaml`: General settings (model, tokens)
- `config/secrets.yaml`: Template for sensitive data
- Create `.secrets.yaml` for your actual secrets (not version controlled)

## Project Structure

```
.
├── config/
│   ├── settings.yaml    # General settings
│   └── secrets.yaml     # Secrets template
├── tools/
│   ├── weather.py       # Weather tool
│   ├── calculator.py    # Calculator tool
│   └── file_search.py   # File search tool
├── main.py             # Main application
├── requirements.txt    # Python dependencies
└── README.md          # This file
