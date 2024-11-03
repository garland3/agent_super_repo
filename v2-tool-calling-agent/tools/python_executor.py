import subprocess
import os
from typing import Dict, Any
import yaml

TOOL_SPEC = {
    "name": "python_executor",
    "description": "Writes Python code to a file and executes it, returning the output",
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The Python code to execute"
            },
            "filename": {
                "type": "string",
                "description": "Name of the file to write the code to (optional, defaults to temp.py)",
                "pattern": "^[a-zA-Z0-9_-]+\\.py$"
            }, 
        },
        "required": ["code"]
    }
}

def load_settings():
    """Load settings from settings.yaml"""
    settings_path = os.path.join("config", "settings.yaml")
    with open(settings_path, 'r') as f:
        settings = yaml.safe_load(f)
    return settings

def python_executor(code: str, filename: str = "temp.py") -> Dict:
    """
    Writes Python code to a file and executes it using the configured conda environment.
    
    Args:
        code (str): The Python code to execute
        filename (str): Name of the file to write the code to (defaults to temp.py)
        
    Returns:
        Dict: Contains either:
            - Success case: {"result": "execution output"}
            - Error case: {"error": "error message"}
    """
    try:
        # Load settings
        settings = load_settings()
        conda_env = settings.get('python_execution', {}).get('conda_env', 'base')

        # Create temp directory if it doesn't exist
        os.makedirs("temp", exist_ok=True)
        file_path = os.path.join("temp", filename)
        
        # Write code to file
        with open(file_path, "w") as f:
            f.write(code)
        
        # Construct the conda activation and Python execution command
        if os.name == 'nt':  # Windows
            command = f"conda activate {conda_env} && python {file_path}"
            shell_cmd = ["cmd", "/c", command]
        else:  # Unix-like
            command = f"conda activate {conda_env} && python {file_path}"
            shell_cmd = ["bash", "-c", command]
        
        # Execute the code and capture output
        result = subprocess.run(
            shell_cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Check for errors
        if result.returncode != 0:
            return {"error": f"Execution failed: {result.stderr}"}
            
        # Return combined output (stdout and stderr)
        output = result.stdout
        if result.stderr:
            output += f"\nErrors/Warnings:\n{result.stderr}"
            
        return {"result": output}
        
    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out after 30 seconds"}
    except Exception as e:
        return {"error": str(e)}
