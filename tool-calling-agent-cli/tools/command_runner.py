import subprocess
from typing import Dict, Any
import sys

TOOL_SPEC = {
    "name": "command_runner",
    "description": "Executes command line commands with user confirmation. Shows command output in real-time.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The command to execute"
            }
        },
        "required": ["command"]
    }
}

def command_runner(command: str) -> Dict[str, Any]:
    """
    Executes a command line command after user confirmation.
    Streams the output in real-time.
    
    Args:
        command (str): The command to execute
        
    Returns:
        Dict: Result dictionary containing either:
            - Success case: {"result": "Command executed successfully"}
            - Error case: {"error": "error message"}
    """
    try:
        # Show command and ask for confirmation
        print(f"\nCommand to execute: {command}")
        confirmation = input("Execute this command? (y/n): ")
        
        if confirmation.lower() != 'y':
            return {"result": "Command execution cancelled by user"}
        
        # Execute command with real-time output
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stream output in real-time
        output = []
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                print(line.rstrip())
                output.append(line)
                
        return_code = process.wait()
        
        if return_code == 0:
            return {"result": "Command executed successfully", "output": "".join(output)}
        else:
            return {"error": f"Command failed with return code {return_code}", "output": "".join(output)}
            
    except Exception as e:
        return {"error": str(e)}
