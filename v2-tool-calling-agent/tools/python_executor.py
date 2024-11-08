import logging
import subprocess
import os
from typing import Dict, Any
import yaml
import ast
from code_database import code_database
from code_summary_generator import get_code_summary, make_code_generic

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    If execution is successful, saves the code to the database.
    
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
        
        # Execute the code with explicit pipe configuration
        process = subprocess.run(
            shell_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Capture output streams
        stdout = process.stdout if process.stdout else ""
        stderr = process.stderr if process.stderr else ""
        
        # Check for errors
        if process.returncode != 0:
            return {"error": f"Execution failed:\nStdout: {stdout}\nStderr: {stderr}"}
            
        # If execution was successful, save to database
        if process.returncode == 0:
            # Extract function signature if present, otherwise wrap in main function
            
            # Make the code more generic and reusable
            generic_code = make_code_generic(code)
            # check if markdown and remove it
            generic_code = generic_code.replace("```python", "").replace("```", "")
            
            # Get code description from LLM
            short_description = get_code_summary(generic_code)
            
            try:
                tree = ast.parse(generic_code)
                has_function = False
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        has_function = True
                        # Found a function definition
                        args = [arg.arg for arg in node.args.args]
                        returns = ""
                        if node.returns:
                            returns = f" -> {ast.unparse(node.returns)}"
                        function_signature = f"def {node.name}({', '.join(args)}){returns}"
                        break
                
                if not has_function:
                    # No function found, wrap code in a main function
                    # Remove any top-level print statements or expressions from signature
                    function_signature = "def main() -> None"
                    # Modify the code to wrap it in a main function
                    generic_code = f"def main() -> None:\n    # Main script functionality\n" + \
                          "\n".join(f"    {line}" for line in generic_code.split("\n")) + \
                          "\n\nif __name__ == '__main__':\n    main()"
            except:
                function_signature = f"def main() -> None"
            
            # Save to database
            db_result = code_database(
                action="add",
                function_signature=function_signature,
                short_description=short_description,
                code=generic_code,  # Save the generalized version
                rating_0_to_5=5,  # Successfully executed code gets a 5 rating
                reason_for_rating="Code executed successfully without errors and was made generic/reusable"
            )
            
            if "error" in db_result:
                print(f"Warning: Failed to save to database: {db_result['error']}")
            
        # Combine output streams with clear separation
        output = ""
        if stdout:
            output += f"Standard Output:\n{stdout}"
        if stderr:
            if output:
                output += "\n"
            output += f"Standard Error:\n{stderr}"
            
        if not output:
            output = "(No output)"
            
        # Log the execution
        logger.info(f"Code executed successfully: {output}")
        return {"result": output}
        
    except subprocess.TimeoutExpired:
        return {"error": "Execution timed out after 30 seconds"}
    except Exception as e:
        return {"error": str(e)}
