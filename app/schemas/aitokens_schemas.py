from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
from datetime import time, datetime

class AITokensCreate(BaseModel):
    conference_id: str
    attendee_id: str
    successful_requests: int
    total_cost: float
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    processing_time: float

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
    # def check_time(cls, v):
    #     current_time = datetime.now().time()
    #     current_time_in_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
    #     processing_time_in_seconds = v.hour * 3600 + v.minute * 60 + v.second
    #     if processing_time_in_seconds < current_time_in_seconds:
    #         raise HTTPException(status_code=400, detail="time cannot be negative")
    #     return v
    
    
    @validator('processing_time')
    # def check_time(cls, v):
    #     if v.timestamp < time():
    #         raise HTTPException(status_code=400, detail="time cannot be negative")
    #     return v
    def check_time(cls, v):
        if v < 0:
            raise HTTPException(status_code=400, detail="time cannot be negative")
        return v

class AITokens(AITokensCreate):
    uuid: str = Field(serialization_alias="id")

    class Config():
        orm_mode = True