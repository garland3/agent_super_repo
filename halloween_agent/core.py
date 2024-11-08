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
from langchain_core.messages import HumanMessage, AIMessage
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

if settings.llm.provider == "ollama":
    # Initialize LLM
    llm = ChatOllama(
        model=settings.llm.model,
        temperature=settings.llm.temperature
    )
elif settings.llm.provider == "together":
    print("Using Together AI")
    from langchain_together import ChatTogether
    llm = ChatTogether(
        model="meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        # api_key="...",
        # other params...
    )
    
    

def manage_image_storage(image_base64):
    """
    Save image to storage and maintain only the last N images
    
    Args:
        image_base64: Base64 encoded image string
    Returns:
        str: Path to the saved image
    """
    try:
        storage_dir = settings.image.storage.dir
        max_images = settings.image.storage.max_images

        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)

        # Generate timestamp-based filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"image_{timestamp}.jpg"
        filepath = os.path.join(storage_dir, filename)

        # Save the new image
        if ';base64,' in image_base64:
            image_base64 = image_base64.split(';base64,')[1]
        image_data = base64.b64decode(image_base64)
        with open(filepath, 'wb') as f:
            f.write(image_data)

        # Get list of existing images sorted by creation time
        existing_images = sorted(
            [os.path.join(storage_dir, f) for f in os.listdir(storage_dir) if f.endswith(('.jpg', '.jpeg', '.png'))],
            key=os.path.getctime
        )

        # Remove oldest images if exceeding max_images
        while len(existing_images) >= max_images:
            oldest_image = existing_images.pop(0)
            os.remove(oldest_image)
            logger.info(f"Removed oldest image: {oldest_image}")

        logger.info(f"Saved new image: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Error in manage_image_storage: {str(e)}\n{traceback.format_exc()}")
        raise ImageProcessingError(f"Failed to manage image storage: {str(e)}")

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



def create_prompt_message(image_base64, text, provider="ollama"):
    """
    Create prompt message with image and text content based on provider
    
    Args:
        image_base64: Base64 encoded image string
        text: Prompt text
        provider: LLM provider ("ollama" or "together")
    Returns:
        list: Formatted messages for the specified provider
    """
    # Handle base64 prefix if present
    if ';base64,' in image_base64:
        image_base64 = image_base64.split(';base64,')[1]
    
    ai_prompt = AIMessage(content="You are a bot that is good at analyzing images.")
    
    if provider == "ollama":
        # Ollama format
        image_part = {
            "type": "image_url",
            "image_url": f"data:image/jpeg;base64,{image_base64}"
        }
        text_part = {"type": "text", "text": text}
        content_parts = [image_part, text_part]
        return [ai_prompt, HumanMessage(content=content_parts)]
    
    elif provider == "together":
        # Together AI format
        return [
            ai_prompt,
            HumanMessage(content=[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                },
                {
                    "type": "text",
                    "text": text
                }
            ])
        ]
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def summarize_image(encoded_image):
    """
    Generate summary of image using LLM
    """
    try:
        logger.info("Starting image summarization")
        if not encoded_image:
            raise LLMProcessingError("No encoded image provided")

        # Save image before processing
        manage_image_storage(encoded_image)

        # Get provider from settings
        provider = settings.llm.provider.lower()

        # Create prompt message
        prompt = settings.llm.prompt if hasattr(settings.llm, 'prompt') else "Describe the contents of this image."
        message = create_prompt_message(encoded_image, prompt, provider)
        
        logger.debug(f"Sending request to LLM using provider: {provider}")
        logger.debug("message: " + str(message))
        
        response = llm.invoke(message)
        logger.info("Successfully received LLM response")
        
        # Handle response
        if hasattr(response, 'content'):
            return response.content
        return str(response)
    
    except Exception as e:
        error_msg = f"Error in LLM processing: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise LLMProcessingError(error_msg)