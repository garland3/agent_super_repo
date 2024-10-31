import base64
import anthropic
from typing import Dict, Any
from pathlib import Path
from dynaconf import Dynaconf

# Load configuration
settings = Dynaconf(
    settings_files=['config/settings.yaml', 'config/secrets.yaml'],
    environments=True
)

# Tool Specification
TOOL_SPEC = {
    "name": "analyze_img_with_claude",
    "description": "Analyzes an image using Claude Vision API and returns a summary based on the user's request",
    "input_schema": {
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "Path to the image file to analyze"
            },
            "request": {
                "type": "string",
                "description": "What to analyze or describe about the image"
            }
        },
        "required": ["image_path", "request"]
    }
}

def analyze_img_with_claude(image_path: str, request: str) -> Dict[str, Any]:
    """
    Analyzes an image using Claude Vision API based on the user's request.
    
    Args:
        image_path (str): Path to the image file
        request (str): What to analyze or describe about the image
        
    Returns:
        Dict: Result dictionary containing either:
            - Success case: {"result": "Claude's analysis"}
            - Error case: {"error": "error message"}
    """
    try:
        # Verify file exists and is an image
        path = Path(image_path)
        if not path.exists():
            return {"error": f"Image file not found: {image_path}"}
            
        # Read and encode image
        with open(path, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode("utf-8")
            
        # Determine media type based on file extension
        media_type = f"image/{path.suffix[1:].lower()}"
        if media_type == "image/jpg":
            media_type = "image/jpeg"
            
        # Initialize Anthropic client
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        
        # Create message with image analysis request
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": request
                        }
                    ],
                }
            ],
        )
        
        # Return Claude's analysis
        return {"result": message.content[0].text}
        
    except Exception as e:
        return {"error": str(e)}
