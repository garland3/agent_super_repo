import os
import pyautogui

# Create Images folder if it doesn't exist
images_folder = os.path.join(os.getcwd(), 'Images') 
if not os.path.exists(images_folder):
    os.makedirs(images_folder)

# Take screenshot and save to Images folder
screenshot = pyautogui.screenshot()
screenshot.save(os.path.join(images_folder, 'screenshot.png'))
print(f"Screenshot saved to: {os.path.join(images_folder, 'screenshot.png')}")