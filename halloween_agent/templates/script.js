// script.js
const video = document.getElementById('video');
const canvas = document.getElementById('drawCanvas');
const ctx = canvas.getContext('2d');
const llmResponse = document.getElementById('llmResponse');
const saveButton = document.getElementById('saveButton');
const processButton = document.getElementById('processButton');

let isProcessing = false;  // Flag to track if a request is in progress
let isDrawing = false;
let startX = 0;
let startY = 0;
let currentBox = null;
let savedBox = null;
let processingInterval = null;

// Initialize webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        // Set canvas size after video loads
        video.onloadedmetadata = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
        };
    })
    .catch(error => {
        console.error('Error accessing webcam:', error);
    });

// Drawing functions
function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function drawBox(x, y, width, height, color = '#00ff00') {
    clearCanvas();
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.strokeRect(x, y, width, height);
    
    // Add semi-transparent fill
    ctx.fillStyle = `${color}33`; // 20% opacity
    ctx.fillRect(x, y, width, height);
}

canvas.addEventListener('mousedown', (e) => {
    if (savedBox) return; // Prevent drawing if box is already saved
    
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    startX = (e.clientX - rect.left) * scaleX;
    startY = (e.clientY - rect.top) * scaleY;
    isDrawing = true;
    saveButton.disabled = true;
});

canvas.addEventListener('mousemove', (e) => {
    if (!isDrawing) return;

    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const currentX = (e.clientX - rect.left) * scaleX;
    const currentY = (e.clientY - rect.top) * scaleY;
    
    const width = currentX - startX;
    const height = currentY - startY;
    
    drawBox(startX, startY, width, height);
});

canvas.addEventListener('mouseup', (e) => {
    if (!isDrawing) return;
    
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    const endX = (e.clientX - rect.left) * scaleX;
    const endY = (e.clientY - rect.top) * scaleY;
    
    const width = endX - startX;
    const height = endY - startY;
    
    currentBox = {
        x: Math.min(startX, endX),
        y: Math.min(startY, endY),
        width: Math.abs(width),
        height: Math.abs(height)
    };
    
    isDrawing = false;
    saveButton.disabled = false;
});

canvas.addEventListener('mouseleave', () => {
    if (isDrawing && !savedBox) {
        isDrawing = false;
        clearCanvas();
        currentBox = null;
        saveButton.disabled = true;
    }
});

saveButton.addEventListener('click', () => {
    if (!currentBox) return;
    
    savedBox = {...currentBox};
    drawBox(savedBox.x, savedBox.y, savedBox.width, savedBox.height, '#ff0000');
    saveButton.disabled = true;
    processButton.disabled = false;
    
    // Update instructions
    const subtitle = document.querySelector('.subtitle');
    subtitle.textContent = 'Click "Start Processing" to begin continuous analysis';
});

processButton.addEventListener('click', () => {
    if (!savedBox) return;
    
    if (processingInterval) {
        // Stop processing
        clearInterval(processingInterval);
        processingInterval = null;
        processButton.textContent = 'Start Processing';
        processButton.style.backgroundColor = '#007bff';
    } else {
        // Start processing
        processingInterval = setInterval(processFrame, 5000);
        processButton.textContent = 'Stop Processing';
        processButton.style.backgroundColor = '#dc3545';
    }
});

async function processFrame() {
    if (isProcessing || !savedBox) {
        console.log('Previous request still processing or no box saved, skipping...');
        return;
    }

    try {
        isProcessing = true;
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = savedBox.width;
        tempCanvas.height = savedBox.height;
        const tempCtx = tempCanvas.getContext('2d');

        // Draw the cropped region from the video
        tempCtx.drawImage(
            video,
            savedBox.x, savedBox.y, savedBox.width, savedBox.height,
            0, 0, savedBox.width, savedBox.height
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
    }
}
