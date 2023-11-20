from openai import OpenAI
from fastapi import UploadFile
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

def upload_file(file: UploadFile):
    global client

    uploaded_file = client.files.create(file=file)
    return uploaded_file

def delete_file(file_id: str):
    global client

    file = client.files.delete(file_id=file_id)
    return file