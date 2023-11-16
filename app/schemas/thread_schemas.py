from pydantic import BaseModel

class Thread(BaseModel):
    models: dict = {}

class ThreadUpdate(BaseModel):
    thread_id: str
    models: dict = {}