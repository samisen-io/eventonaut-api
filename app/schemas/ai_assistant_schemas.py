from pydantic import BaseModel, validator
from fastapi import HTTPException
from typing import List

class AssistantCreate(BaseModel):
    model: str
    name: str | None = None
    description: str | None = None
    instructions: str | None = None
    tools: List = []
    file_ids: List = []
    metadata: dict = {}

    @validator('model')
    def model_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid model")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Model too long")
        return v

    @validator('name')
    def name_is_not_empty(cls, v):
        if v is not None and v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v
    
    @validator('description')
    def description_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid description")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Description too long")
        return v
    
    @validator('instructions')
    def instructions_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid instructions")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Instructions too long")
        return v
    
class AssistantUpdate(BaseModel):
    assistant_id: str
    model: str | None = None
    name: str | None = None
    description: str | None = None
    instructions: str | None = None
    tools: List = []
    file_ids: List = []
    metadata: dict = {}

    @validator('assistant_id')
    def assistant_id_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid id")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Id too long")
        return v

    @validator('model')
    def model_is_not_empty(cls, v):
        if v is not None and v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid model")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Model too long")
        return v

    @validator('name')
    def name_is_not_empty(cls, v):
        if v is not None and v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v
    
    @validator('description')
    def description_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid description")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Description too long")
        return v
    
    @validator('instructions')
    def instructions_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid instructions")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Instructions too long")
        return v