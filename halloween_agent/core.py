import os
import base64
import logging
import traceback
from datetime import datetime
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from dynaconf import Dynaconf

# Initialize settings
settings = Dynaconf(
    settings_files=['settings.yaml'],
)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Custom exceptions
class ImageProcessingError(Exception):
    """Custom exception for image processing errors"""
    pass

class LLMProcessingError(Exception):
    """Custom exception for LLM processing errors"""
    pass

# Initialize LLM
llm = ChatOllama(
    model=settings.llm.model,
    temperature=settings.llm.temperature
)

def convert_to_base64(pil_image):
    """
    Convert PIL images to Base64 encoded strings
    
    Args:
        pil_image: PIL image
    Returns:
        str: Base64 encoded string
    """
    try:
        logger.debug("Starting PIL image encoding process")
        if pil_image is None:
            raise ImageProcessingError("Input PIL image is None")
        
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        logger.debug("Successfully encoded PIL image to base64")
        return img_str
    
    except Exception as e:
        logger.error(f"Error in convert_to_base64: {str(e)}\n{traceback.format_exc()}")
        raise ImageProcessingError(f"Failed to encode PIL image: {str(e)}")

def encode_image(image_np):
    """
    Encode numpy array image to base64 string
    """
    try:
        logger.debug("Starting image encoding process")
        if image_np is None:
            raise ImageProcessingError("Input image is None")
        
        # Convert numpy array to PIL Image
        pil_image = Image.fromarray(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB))
        return convert_to_base64(pil_image)
    
    except Exception as e:
        logger.error(f"Error in encode_image: {str(e)}\n{traceback.format_exc()}")
        raise ImageProcessingError(f"Failed to encode image: {str(e)}")

def decode_image(image_base64):
    """
    Decode base64 string to numpy array image
    """
    try:
        logger.debug("Starting image decoding process")
        if not image_base64:
            raise ImageProcessingError("No image data provided")
        
        # Remove base64 prefix if it exists
        if ';base64,' in image_base64:
            image_base64 = image_base64.split(';base64,')[1]
        
        image_bytes = base64.b64decode(image_base64)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ImageProcessingError("Failed to decode image data")
        
        logger.debug("Successfully decoded base64 to image")
        return img
    
    except Exception as e:
        logger.error(f"Error in decode_image: {str(e)}\n{traceback.format_exc()}")
        raise ImageProcessingError(f"Failed to decode image: {str(e)}")

def create_prompt_message(image_base64, text):
    """
    Create prompt message with image and text content
    """
    image_part = {
        "type": "image_url",
        "image_url": f"data:image/jpeg;base64,{image_base64}"
    }
    text_part = {"type": "text", "text": text}
    content_parts = [image_part, text_part]
    return HumanMessage(content=content_parts)

def summarize_image(encoded_image):
    """
    Generate summary of image using LLM
    """
    try:
        logger.info("Starting image summarization")
        if not encoded_image:
            raise LLMProcessingError("No encoded image provided")

        # Remove base64 prefix if it exists
        if ';base64,' in encoded_image:
            encoded_image = encoded_image.split(';base64,')[1]

        # Create prompt message
        prompt = settings.llm.prompt
        message = create_prompt_message(encoded_image, prompt)
        
        logger.debug("Sending request to LLM")
        response = llm.invoke([message])
        logger.info("Successfully received LLM response")
        
        # Handle response
        if hasattr(response, 'content'):
            return response.content
        return str(response)
    
    except Exception as e:
        error_msg = f"Error in LLM processing: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise LLMProcessingError(error_msg)
