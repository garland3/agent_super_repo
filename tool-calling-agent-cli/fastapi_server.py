from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import logging
import time
from datetime import datetime
from claude_processor import ClaudeProcessor, IOHandler
from utils import load_tool_specs, load_prompt_template

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Load tools
tools = load_tool_specs()
prompt_template = load_prompt_template()

# Create a dictionary to store processor instances and their logs for each session
processors = {}
session_logs = {}

def web_input() -> str:
    # This is a placeholder - actual input comes from the request
    return ""

def web_output(message: str):
    # This is a placeholder - actual output is handled by the template
    pass

def web_log(session_id: str, message: str):
    if session_id not in session_logs:
        session_logs[session_id] = []
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    session_logs[session_id].append(formatted_message)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "response": None,
        "tools": tools,
        "logs": []
    })

@app.post("/process", response_class=HTMLResponse)
async def process(request: Request, user_input: str = Form(...)):
    try:
        # Create or get processor for this session
        session_id = str(hash(request.client.host))
        if session_id not in processors:
            io_handler = IOHandler(
                web_input, 
                web_output, 
                lambda msg: web_log(session_id, msg)
            )
            processors[session_id] = ClaudeProcessor(io_handler)
            session_logs[session_id] = []
        
        processor = processors[session_id]
        
        # Process input and get response
        start_time = time.time()
        response = processor.process_user_input(user_input, tools, prompt_template)
        elapsed_time = time.time() - start_time
        web_log(session_id, f"⏱️ Total processing time: {elapsed_time:.2f} seconds")

        # Get logs for this session
        logs = session_logs.get(session_id, [])

        return templates.TemplateResponse("index.html", {
            "request": request,
            "response": response,
            "previous_input": user_input,
            "tools": tools,
            "logs": logs
        })
        
    except Exception as e:
        logging.error(f"Error occurred: {e}", exc_info=True)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "response": f"Error: {str(e)}",
            "previous_input": user_input,
            "tools": tools,
            "logs": session_logs.get(session_id, [])
        })

if __name__ == "__main__":
    uvicorn.run("fastapi_server:app", host="127.0.0.1", port=8000, reload=True)
