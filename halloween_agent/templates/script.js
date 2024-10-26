// script.js
const video = document.getElementById('video');
const canvas = document.getElementById('drawCanvas');
const ctx = canvas.getContext('2d');
const llmResponse = document.getElementById('llmResponse');
const processButton = document.getElementById('processButton');
let isProcessing = false;

// Drawing state
let isDrawing = false;
let startX = 0;
let startY = 0;
let currentBox = null;

// Initialize webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(error => {
        console.error('Error accessing webcam:', error);
    });

// Drawing functions
function drawBox(x, y, width, height) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = '#00ff00';
    ctx.lineWidth = 2;
    ctx.strokeRect(x, y, width, height);
}

canvas.addEventListener('mousedown', (e) => {
    const rect = canvas.getBoundingClientRect();
    startX = e.clientX - rect.left;
    startY = e.clientY - rect.top;
    isDrawing = true;
    processButton.disabled = true;
});

canvas.addEventListener('mousemove', (e) => {
    if (!isDrawing) return;

    const rect = canvas.getBoundingClientRect();
    const currentX = e.clientX - rect.left;
    const currentY = e.clientY - rect.top;
    
    const width = currentX - startX;
    const height = currentY - startY;
    
    drawBox(startX, startY, width, height);
});

canvas.addEventListener('mouseup', (e) => {
    if (!isDrawing) return;
    
    const rect = canvas.getBoundingClientRect();
    const endX = e.clientX - rect.left;
    const endY = e.clientY - rect.top;
    
    const width = endX - startX;
    const height = endY - startY;
    
    currentBox = {
        x: Math.min(startX, endX),
        y: Math.min(startY, endY),
        width: Math.abs(width),
        height: Math.abs(height)
    };
    
    isDrawing = false;
    processButton.disabled = false;
});

canvas.addEventListener('mouseleave', () => {
    if (isDrawing) {
        isDrawing = false;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        currentBox = null;
        processButton.disabled = true;
    }
});

async function processFrame() {
    if (isProcessing || !currentBox) return;

    try {
        isProcessing = true;
        processButton.disabled = true;

        // Create a temporary canvas for the cropped region
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = currentBox.width;
        tempCanvas.height = currentBox.height;
        const tempCtx = tempCanvas.getContext('2d');

        // Draw the cropped region from the video
        tempCtx.drawImage(
            video,
            currentBox.x, currentBox.y, currentBox.width, currentBox.height,
            0, 0, currentBox.width, currentBox.height
        );

        // Convert canvas to base64 string, removing the data:image/png;base64, prefix
        const base64Image = tempCanvas.toDataURL('image/png').split(',')[1];

        const formData = new FormData();
        formData.append('image', base64Image);

        const response = await fetch('/process_image', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Create separator
        const separator = document.createElement('p');
        separator.textContent = '-----------';
        
        // Create message element
        const p = document.createElement('p');
        p.textContent = data.llm_response;
        
        // Insert both elements
        llmResponse.insertBefore(separator, llmResponse.firstChild);
        llmResponse.insertBefore(p, llmResponse.firstChild);
    } catch (error) {
        console.error('Error processing image:', error);
    } finally {
        isProcessing = false;
        processButton.disabled = false;
    }
}

// Add click handler for process button
processButton.addEventListener('click', processFrame);
