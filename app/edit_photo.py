import os
from fastapi import HTTPException, status
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
clipdrop_api_key = os.getenv('CLIPDROP_API_KEY')
if not clipdrop_api_key:
    raise HTTPException(status_code=500, detail="CLIPDROP_API_KEY not set")

def remove_background(file_object, filename):
    file_extension = filename.split(".")[-1]
    r = requests.post('https://clipdrop-api.co/remove-background/v1',
                  files = {
                      'image_file': (filename, file_object, f'image/{file_extension}'),
                  },
                  headers = {'x-api-key': clipdrop_api_key},)
    if r.ok:
        result = r.content
    else: 
        status_code = r.status_code
        print(filename)
        print(f'image/{file_extension}')
        raise HTTPException(status_code=status_code, detail="Failed to remove background")
    return result

def check_the_file_size(file_object):
    file_size = len(file_object)
    max_file_size = 5 * 1024 * 1024
    if file_size > max_file_size:
        logging.exception(f"The file size cannot exceed {max_file_size} bytes.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size too large")
    
def check_the_file_type(filename):
    file_extension = filename.split(".")[-1]
    if file_extension not in ["jpg", "jpeg", "png", "webp"]: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only jpg, jpeg, png and webp are allowed.")