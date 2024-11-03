import os
import importlib
from typing import Dict, List

def load_prompt_template() -> str:
    """Load the prompt template from file"""
    with open('prompts/prompt_template.txt', 'r', encoding='utf-8') as f:
        return f.read()

def load_system_prompt() -> str:
    """Load the system prompt from file"""
    with open('prompts/system_prompt.txt', 'r', encoding='utf-8') as f:
        return f.read()

def load_tool_specs() -> List[Dict]:
    """Load tool specifications from all tool modules"""
    tools_dir = 'tools'
    tool_specs = []
    
    # Get all Python files in tools directory
    tool_files = [f[:-3] for f in os.listdir(tools_dir) 
                 if f.endswith('.py') and f != '__init__.py']
    
    # Import each tool module and get its specification
    for tool_file in tool_files:
        module = importlib.import_module(f'tools.{tool_file}')
        if hasattr(module, 'TOOL_SPEC'):
            tool_specs.append(module.TOOL_SPEC)
    
    return tool_specs

def _load_tool_functions() -> Dict:
    """Dynamically load all tool functions from the tools directory"""
    tools_dir = 'tools'
    tool_functions = {}
    
    # Get all Python files in tools directory
    tool_files = [f[:-3] for f in os.listdir(tools_dir) 
                 if f.endswith('.py') and f != '__init__.py']
    
    # Import each tool module and get its main function
    for tool_file in tool_files:
        module = importlib.import_module(f'tools.{tool_file}')
        if hasattr(module, 'TOOL_SPEC'):
            tool_name = module.TOOL_SPEC['name']
            # Get the main function that matches the tool name
            if hasattr(module, tool_name):
                tool_functions[tool_name] = getattr(module, tool_name)
    
    return tool_functions

# Create a global mapping of tool names to their functions
TOOL_FUNCTIONS = _load_tool_functions()

def handle_tool_call(tool_use: Dict) -> Dict:
    """Execute the appropriate tool based on the tool use from Claude"""
    tool_name = tool_use.get("name")
    arguments = tool_use.get("input", {})
    
    if tool_name in TOOL_FUNCTIONS:
        return TOOL_FUNCTIONS[tool_name](**arguments)
    else:
        return {"error": f"Unknown tool: {tool_name}"}
