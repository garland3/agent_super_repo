from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import yaml
import httpx
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load settings
try:
    with open('settings.yaml', 'r') as f:
        settings = yaml.safe_load(f)
    logger.info("Settings loaded successfully")
except Exception as e:
    logger.error(f"Failed to load settings: {str(e)}")
    raise

app = FastAPI(title="LLM Function Calling API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class QueryRequest(BaseModel):
    query: str = Field(description="The user's query")

# Define available tools
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get the weather for, e.g. San Francisco, CA"
                    },
                    "format": {
                        "type": "string",
                        "description": "The format to return the weather in",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location", "format"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_person_info",
            "description": "Extract information about a person from text",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The person's name"
                    },
                    "height": {
                        "type": "number",
                        "description": "The person's height in feet"
                    },
                    "hair_color": {
                        "type": "string",
                        "description": "The person's hair color"
                    }
                },
                "required": ["name", "height", "hair_color"]
            }
        }
    }
]

@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    return FileResponse('static/index.html')

@app.post("/query")
async def process_query(request: QueryRequest):
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Prepare the request to Ollama
        ollama_request = {
            "model": settings['model']['name'],
            "messages": [
                {
                    "role": "user",
                    "content": request.query
                }
            ],
            "stream": False,
            "tools": TOOLS
        }
        
        # Make request to Ollama
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:11434/api/chat",
                json=ollama_request
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Ollama API error: {response.text}"
                )
            
            result = response.json()
            logger.info(f"Got response from Ollama: {result}")
            
            return result
            
    except httpx.RequestError as e:
        logger.error(f"An error occurred while requesting Ollama API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=f"HTTP error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings['server']['host'], 
        port=settings['server']['port']
    )
