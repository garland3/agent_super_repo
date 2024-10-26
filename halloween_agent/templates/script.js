// script.js
const video = document.getElementById('video');
const llmResponse = document.getElementById('llmResponse');
let isProcessing = false;  // Flag to track if a request is in progress

navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(error => {
        console.error('Error accessing webcam:', error);
    });

async function processFrame() {
    if (isProcessing) {
        console.log('Previous request still processing, skipping...');
        return;
    }

    try {
        isProcessing = true;
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);

        // Convert canvas to base64 string, removing the data:image/png;base64, prefix
        const base64Image = canvas.toDataURL('image/png').split(',')[1];

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
        llmResponse.insertBefore(p, llmResponse.firstChild); // Add new messages to the top
    } catch (error) {
        console.error('Error processing image:', error);
    } finally {
        isProcessing = false;
    }
}

// Run processFrame every 5 seconds
setInterval(processFrame, 5000);
