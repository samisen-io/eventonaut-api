from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
from datetime import time

class AITokensCreate(BaseModel):
    conference_id: str
    attendee_id: str
    successful_requests: int
    total_cost: int
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    processing_time: time

    @validator('conference_id', 'attendee_id')
    def check_id(cls, v):
        if v == "" or v == "string" or v == "None" or v.strip() == "":
            raise HTTPException(status_code=400, detail="id cannot be empty")
        return v

    @validator('successful_requests', 'total_cost', 'total_tokens', 'prompt_tokens', 'completion_tokens')
    def check_positive(cls, v):
        if v < 0:
            raise HTTPException(status_code=400, detail="must be positive")
        return v
    
    @validator('processing_time')
    def check_time(cls, v):
        if v < time():
            raise HTTPException(status_code=400, detail="time cannot be negative")
        return v

class AITokens(AITokensCreate):
    uuid: str = Field(serialization_alias="id")

    class Config():
        orm_mode = True