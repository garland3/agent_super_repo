import os

directory = r'C:\Users\garla\Downloads'

image_extensions = ['.jpg', '.png', '.gif', '.bmp', '.tiff', '.jpeg']

image_files = [f for f in os.listdir(directory) 
               if os.path.isfile(os.path.join(directory, f)) 
               and os.path.splitext(f)[1].lower() in image_extensions]

num_images = len(image_files)

print(f'There are {num_images} image files in {directory}')