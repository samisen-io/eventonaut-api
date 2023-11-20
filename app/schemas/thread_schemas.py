from pydantic import BaseModel

class Thread(BaseModel):
    models: dict | None = None

class ThreadUpdate(BaseModel):
    thread_id: str
    models: dict | None = None