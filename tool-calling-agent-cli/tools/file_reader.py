from typing import Dict
import os

class FileReader:
    def execute(self, arguments: Dict) -> Dict:
        """
        Read contents of a file
        
        Arguments:
            path: str - Path to the file to read
            
        Returns:
            Dict containing the file contents or error message
        """
        try:
            path = arguments.get("path")
            
            if not path:
                return {"error": "File path not specified"}
                
            if not os.path.exists(path):
                return {"error": f"File not found: {path}"}
                
            with open(path, 'r') as file:
                content = file.read()
                
            return {
                "content": content
            }
            
        except Exception as e:
            return {"error": str(e)}
