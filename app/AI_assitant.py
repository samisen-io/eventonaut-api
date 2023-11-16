from openai import OpenAI
import os
import logging
from fastapi import UploadFile, HTTPException
from .schemas import ai_assistant_schemas as schemas
from .schemas import thread_schemas

client = OpenAI()

def create_assistant(schema: schemas.AssistantCreate):
    global client
    assistant = client.beta.assistants.create(**schema.model_dump())
    return assistant

def get_assistant(assistant_id: str):
    global client
    assistant = client.beta.assistants.retrieve(assistant_id)
    return assistant

def update_assistant(schema: schemas.AssistantUpdate):
    global client

    updates= {}

    for key, value in schema.model_dump().items():
        if value is not None:
            updates[key] = value

    assistant = client.beta.assistants.update(**updates)
    return assistant

def delete_assistant(assistant_id: str):
    global client
    assistant = client.beta.assistants.delete(assistant_id)
    return assistant

def list_assistants():
    global client
    assistants = client.beta.assistants.list()
    return assistants

def create_thread(schema: thread_schemas.Thread):
    global client
    return client.beta.threads.create(**schema.model_dump())

def get_thread(thread_id: str):
    global client
    return client.beta.threads.retrieve(thread_id)

def update_thread(schema: thread_schemas.ThreadUpdate):
    global client

    updates= {}

    for key, value in schema.model_dump().items():
        if value is not None:
            updates[key] = value

    return client.beta.threads.update(**updates)

def delete_thread(thread_id: str):
    global client
    return client.beta.threads.delete(thread_id)

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