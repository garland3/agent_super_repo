import os
import glob
from typing import Dict

# Tool specification
TOOL_SPEC = {
    "name": "search_files",
    "description": "Search for files in a directory",
    "input_schema": {
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "Directory path to search in"
            },
            "pattern": {
                "type": "string",
                "description": "Search pattern (e.g., *.txt, *.py)"
            }
        },
        "required": ["directory", "pattern"]
    }
}

def search_files(directory: str, pattern: str) -> Dict:
    """
    Search for files in a directory
    
    Args:
        directory (str): Directory to search in
        pattern (str): Search pattern (e.g., *.txt, *.py)
        
    Returns:
        Dict: List of matching files or error message
    """
    try:
        if not os.path.exists(directory):
            return {"error": f"Directory not found: {directory}"}
            
        search_path = os.path.join(directory, pattern)
        matching_files = glob.glob(search_path)
        
        return {
            "files": matching_files,
            "count": len(matching_files)
        }
        
    except Exception as e:
        return {"error": str(e)}
