# Project Goal

This project aims to build a web application that leverages a vision-based Large Language Model (LLM) to analyze images captured from a user's webcam.  The application captures an image from the webcam every 5 seconds, sends it to the LLM for analysis, and displays the LLM's response in a textbox below the video feed. The textbox is designed to display the most recent responses at the top, with older messages appearing further down, creating a chronological history of the LLM's interpretations.

The application uses FastAPI for the backend, handling image uploads and communication with the LLM. The frontend, built with HTML and JavaScript, manages webcam access, image capture, and displaying the LLM's responses.  The `langchain_together` library facilitates interaction with the chosen vision LLM (meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo).  The application is designed to be user-friendly, requiring minimal setup and providing real-time analysis of webcam imagery.


if it hangs, then 

pkill -9 -f uvicorn

