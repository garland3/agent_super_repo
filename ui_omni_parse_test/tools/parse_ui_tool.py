from typing import Dict, Any
import requests
from PIL import ImageGrab
import os
import json

# Tool Specification
TOOL_SPEC = {
    "name": "parse_ui",
    "description": "Takes a screenshot of the current screen, sends it to a UI parsing server, and returns the parsed elements and their locations",
    "input_schema": {
        "type": "object",
        "properties": {
            "box_threshold": {
                "type": "number",
                "description": "Threshold for box detection confidence (0-1)",
                "minimum": 0,
                "maximum": 1
            },
            "iou_threshold": {
                "type": "number",
                "description": "Threshold for Intersection over Union in object detection (0-1)",
                "minimum": 0,
                "maximum": 1
            }
        },
        "required": []  # Both parameters are optional
    }
}

def parse_ui(box_threshold: float = 0.05, iou_threshold: float = 0.1) -> Dict:
    """
    Takes a screenshot and sends it to the UI parsing server for analysis
    
    Args:
        box_threshold (float): Threshold for box detection confidence (0-1)
        iou_threshold (float): Threshold for Intersection over Union (0-1)
        
    Returns:
        Dict: Result dictionary containing either:
            - Success case: {
                "result": {
                    "annotated_image": str,  # Base64 encoded image
                    "parsed_content": str,    # Parsed UI elements
                    "coordinates": str        # Element coordinates
                }
            }
            - Error case: {"error": "error message"}
    """
    try:
        # Create imgs directory if it doesn't exist
        os.makedirs('imgs', exist_ok=True)
        
        # Take screenshot and save
        screenshot = ImageGrab.grab()
        screenshot_path = 'imgs/temp_screenshot.png'
        screenshot.save(screenshot_path)
        
        # Prepare the files and data for the request
        url = 'http://localhost:8000/process'
        files = {
            'file': ('screenshot.png', open(screenshot_path, 'rb'), 'image/png')
        }
        data = {
            'box_threshold': str(box_threshold),
            'iou_threshold': str(iou_threshold)
        }
        
        # Send request to server
        response = requests.post(url, files=files, data=data)
        
        # Clean up the temporary screenshot
        # files['file'][1].close()
        # os.remove(screenshot_path)
        
        # Check if request was successful
        if response.status_code == 200:
            return {"result": response.json()}
        else:
            return {"error": f"Server returned status code {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"error": str(e)}
