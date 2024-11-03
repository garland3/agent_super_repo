import subprocess
from typing import Dict, Optional

TOOL_SPEC = {
    "name": "execute_powershell",
    "description": "Execute a PowerShell command on Windows systems and return its output",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The PowerShell command to execute"
            },
            "working_dir": {
                "type": "string",
                "description": "Working directory for command execution (optional)"
            }
        },
        "required": ["command"]
    }
}

def execute_powershell(command: str, working_dir: Optional[str] = None) -> Dict:
    """
    Execute a PowerShell command and return its output
    
    Args:
        command (str): PowerShell command to execute
        working_dir (str, optional): Working directory for command execution
        
    Returns:
        Dict: Contains either:
            - Success: {"result": "command output"}
            - Error: {"error": "error message"}
    """
    try:
        # Construct PowerShell command with proper arguments
        powershell_command = ["powershell", "-NoProfile", "-NonInteractive", "-Command", command]
        
        # Execute command with specified working directory if provided
        process = subprocess.run(
            powershell_command,
            capture_output=True,
            text=True,
            cwd=working_dir,
            check=True
        )
        
        # Return stdout if successful
        return {"result": process.stdout}
        
    except subprocess.CalledProcessError as e:
        # Return stderr if command failed
        return {"error": f"PowerShell command failed: {e.stderr}"}
    except Exception as e:
        # Return generic error for other failures
        return {"error": f"PowerShell execution failed: {str(e)}"}
