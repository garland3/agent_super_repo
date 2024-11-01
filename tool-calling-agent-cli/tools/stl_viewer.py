import os
from typing import Dict
from pathlib import Path

# Tool Specification
TOOL_SPEC = {
    "name": "view_stl",
    "description": "View an STL file in the browser using Three.js",
    "input_schema": {
        "type": "object",
        "properties": {
            "stl_path": {
                "type": "string",
                "description": "Path to the STL file to view"
            }
        },
        "required": ["stl_path"]
    }
}

def view_stl(stl_path: str) -> Dict:
    """
    Creates a temporary HTML file to view the STL file and launches it in the browser.
    
    Args:
        stl_path (str): Path to the STL file to view
        
    Returns:
        Dict: Result dictionary containing either:
            - Success case: Path to the generated HTML file and browser launch command
            - Error case: {"error": "error message"}
    """
    try:
        # Verify STL file exists
        if not os.path.exists(stl_path):
            return {"error": f"STL file not found: {stl_path}"}
            
        # Get absolute path and convert to file URL
        abs_path = os.path.abspath(stl_path)
        file_url = f"file:///{abs_path.replace(os.sep, '/')}"
        
        # Read the template
        template_path = os.path.join(os.path.dirname(__file__), "stl_viewer_template.html")
        with open(template_path, 'r') as f:
            template_content = f.read()
            
        # Replace the placeholder with the STL file path
        html_content = template_content.replace('{stl_path}', file_url)
        
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.path.dirname(__file__), "..", "temp")
        os.makedirs(output_dir, exist_ok=True)
        
        # Write the viewer HTML
        output_path = os.path.join(output_dir, "stl_viewer.html")
        with open(output_path, 'w') as f:
            f.write(html_content)
            
        # Convert output path to file URL for browser
        output_url = f"file:///{output_path.replace(os.sep, '/')}"
            
        return {
            "result": {
                "message": "STL viewer created successfully",
                "viewer_path": output_path,
                "launch_url": output_url,
                "browser_action": {
                    "action": "launch",
                    "url": output_url
                }
            }
        }
        
    except Exception as e:
        return {"error": str(e)}
