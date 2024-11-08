from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import torch
from PIL import Image
import io
import base64
from typing import Optional
import numpy as np

from utils import check_ocr_box, get_yolo_model, get_caption_model_processor, get_som_labeled_img
from ultralytics import YOLO
from transformers import AutoProcessor, AutoModelForCausalLM

app = FastAPI(title="OmniParser API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure templates
templates = Jinja2Templates(directory="templates")

# Load models at startup
print("Loading models...")
yolo_model = YOLO('weights/icon_detect/best.pt').to('cuda')
processor = AutoProcessor.from_pretrained("microsoft/Florence-2-base", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("weights/icon_caption_florence", torch_dtype=torch.float16, trust_remote_code=True).to('cuda')
caption_model_processor = {'processor': processor, 'model': model}
print('Models loaded successfully!')

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process")
async def process_image(
    file: UploadFile = File(...),
    box_threshold: float = Form(0.05),
    iou_threshold: float = Form(0.1)
):
    try:
        # Read and save the uploaded image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes))
        temp_path = 'imgs/temp_image.png'
        image.save(temp_path)

        # Calculate box overlay ratio based on image size
        box_overlay_ratio = image.size[0] / 3200
        draw_bbox_config = {
            'text_scale': 0.8 * box_overlay_ratio,
            'text_thickness': max(int(2 * box_overlay_ratio), 1),
            'text_padding': max(int(3 * box_overlay_ratio), 1),
            'thickness': max(int(3 * box_overlay_ratio), 1),
        }

        # Process the image
        ocr_bbox_rslt, is_goal_filtered = check_ocr_box(
            temp_path, 
            display_img=False, 
            output_bb_format='xyxy', 
            goal_filtering=None, 
            easyocr_args={'paragraph': False, 'text_threshold': 0.9},
            use_paddleocr=True
        )
        text, ocr_bbox = ocr_bbox_rslt

        # Get labeled image and parsed content
        dino_labled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
            temp_path,
            yolo_model,
            BOX_TRESHOLD=box_threshold,
            output_coord_in_ratio=True,
            ocr_bbox=ocr_bbox,
            draw_bbox_config=draw_bbox_config,
            caption_model_processor=caption_model_processor,
            ocr_text=text,
            iou_threshold=iou_threshold
        )

        # Convert parsed content list to string
        parsed_content = '\n'.join(parsed_content_list)

        # Return the results
        return JSONResponse({
            "annotated_image": dino_labled_img,  # Base64 encoded image
            "parsed_content": parsed_content,
            "coordinates": str(label_coordinates)
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
