from openai import OpenAI
import os
import logging
from fastapi import UploadFile, HTTPException

client = OpenAI()

def create_assistant(name: str):
    global client
    assistant = client.beta.assistants.create(
        name=name,
        model="gpt-4-1106-preview",
        instructions="You are conference assitant. You can help users with their queries related to the sessions of the conference to build their agenda/schedule."
    )
    return assistant


def file_upload(file: UploadFile):
    global client

    app_folder = 'app'

    files_folder = os.path.join(app_folder, 'files')

    if not os.path.exists(files_folder):
        os.makedirs(files_folder)
    
    if file.filename.endswith(".csv") or file.filename.endswith(".json") or file.filename.endswith(".xlsx"):
        if file.filename.endswith(".csv"):
            file_path = os.path.join(files_folder, 'sessions.csv')
        elif file.filename.endswith(".json"):
            file_path = os.path.join(files_folder, 'sessions.json')
        elif file.filename.endswith(".xlsx"):
            file_path = os.path.join(files_folder, 'sessions.xlsx')

        logging.info("Uploading file to %s" % file_path)
        
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        logging.info("File uploaded successfully")
    else:
        raise HTTPException(status_code=400, detail="File format not supported")

    uploaded_file = client.files.create(file=file)
    return uploaded_file

def create_thread():
    global client
    return client.beta.threads.create()