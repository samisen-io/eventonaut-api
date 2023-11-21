from pydantic import BaseModel

class Thread(BaseModel):
    metadata: dict | None = None

class ThreadUpdate(BaseModel):
    thread_id: str
    metadata: dict | None = None