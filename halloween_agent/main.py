from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import logging
import asyncio
import base64
from PIL import Image
import io
from core import summarize_image, ImageProcessingError, LLMProcessingError
from dynaconf import Dynaconf

# Initialize settings
settings = Dynaconf(
    settings_files=['settings.yaml'],
)

# Get logger
logger = logging.getLogger(__name__)

app = FastAPI()
# Change the static files mount point to /static instead of root
app.mount("/static", StaticFiles(directory="templates"), name="static")

# Add templates directory for serving HTML files
templates = Jinja2Templates(directory="templates")

def validate_base64_image(base64_str: str) -> bool:
    """
    Validate if the string is a proper base64 encoded image
    Returns True if valid, False otherwise
    """
    try:
        # Remove header if present
        if ';base64,' in base64_str:
            base64_str = base64_str.split(';base64,')[1]
        
        # Try to decode base64
        image_data = base64.b64decode(base64_str)
        
        # Try to open as image
        img = Image.open(io.BytesIO(image_data))
        
        # Check if image is too large
        max_size = settings.image.max_size_mb * 1024 * 1024  # Convert MB to bytes
        if len(image_data) > max_size:
            logger.error("Image size too large")
            return False
            
        # Validate image dimensions
        width, height = img.size
        if width > settings.image.max_width or height > settings.image.max_height:
            logger.error(f"Image dimensions too large: {width}x{height}")
            return False
            
        # Check if image format is supported
        if img.format.lower() not in settings.image.supported_formats:
            logger.error(f"Unsupported image format: {img.format}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Image validation error: {str(e)}")
        return False

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    logger.info("Serving root endpoint")
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process_image")
async def process_image(request: Request):
    """
    Process uploaded image and return LLM analysis
    """
    logger.info("Starting new image processing request")
    try:
        form = await request.form()
        image = form.get("image")
        
        if not image:
            logger.warning("No image data received in request")
            raise HTTPException(status_code=400, detail="No image data provided")

        # Validate image format and size
        if not validate_base64_image(image):
            raise HTTPException(status_code=400, detail="Invalid image format or size")

        encoded_image = image
        
        # Run LLM analysis in a separate thread with timeout
        logger.info("Getting LLM analysis")
        loop = asyncio.get_event_loop()
        try:
            llm_response = await asyncio.wait_for(
                loop.run_in_executor(None, summarize_image, encoded_image),
                timeout=settings.llm.timeout_seconds
            )
        except asyncio.TimeoutError:
            logger.error("LLM processing timeout")
            raise HTTPException(status_code=504, detail="Processing timeout")
        
        logger.info("Successfully processed image and generated response")
        return {"llm_response": llm_response}

    except ImageProcessingError as e:
        error_msg = f"Image processing error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    
    except LLMProcessingError as e:
        error_msg = f"LLM processing error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
