from typing import Dict, Any
import os

TOOL_SPEC = {
    "name": "file_writer",
    "description": "Write or append text content to a file. Creates parent directories if they don't exist.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to write to"
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file"
            },
            "append": {
                "type": "boolean",
                "description": "If true, append content to file. If false, overwrite file.",
                "default": False
            }
        },
        "required": ["path", "content"]
    }
}

def file_writer(path: str, content: str, append: bool = False) -> Dict[str, Any]:
    """
    Write or append content to a file, creating parent directories if needed.
    
    Args:
        path (str): Path to the file to write to
        content (str): Content to write to the file
        append (bool): If True, append to file. If False, overwrite file.
        
    Returns:
        Dict[str, Any]: Result dictionary containing either:
            - Success: {"result": "File written successfully"}
            - Error: {"error": error message}
    """
    try:
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        
        # Write or append content to file
        mode = 'a' if append else 'w'
        with open(path, mode, encoding='utf-8') as f:
            f.write(content)
            
        return {"result": "File written successfully"}
        
    except Exception as e:
        return {"error": str(e)}
