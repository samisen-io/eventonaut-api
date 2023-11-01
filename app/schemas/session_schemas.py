from pydantic import BaseModel, validator
from fastapi import HTTPException
from datetime import date as Date, time

#pydantic model for session create
class SessionCreate(BaseModel):
    conference_id:int
    name: str
    start_time: time
    end_time: time
    description: str 
    date: Date
    location: str 

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if v is None or v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid name")
        return v
    
    @validator('start_time')
    def start_time_must_not_be_empty(cls, v):
        if v is None or v == "":
            raise HTTPException(status_code=400, detail="Invalid start time")
        return v
    
    @validator('end_time')
    def end_time_must_not_be_empty(cls, v):
        if v is None or v == "":
            raise HTTPException(status_code=400, detail="Invalid end time")
        return v
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        if v is None or v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid description")
        return v
    
    @validator('date')
    def date_must_not_be_empty(cls, v):
        if v is None or v == "":
            raise HTTPException(status_code=400, detail="Invalid date")
        return v
    
    @validator('location')
    def location_must_not_be_empty(cls, v):
        if v is None or v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid location")
        return v
    
    @validator('conference_id')
    def conference_id_must_not_be_empty(cls, v):
        if v is None and v <= 0:
            raise HTTPException(status_code=400, detail="Invalid conference id")
        return v

#pydantic model for session
class Session(SessionCreate):
    id: int
    owner_id: int
    class Config:
        orm_mode = True

#pydantic model for session update
class SessionUpdate(BaseModel):
    id: int
    conference_id:int
    name: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    description: str | None = None
    date: Date | None = None
    location: str | None = None

    @validator('id')
    def id_must_not_be_empty(cls, v):
        if v is None or v <= 0:
            raise HTTPException(status_code=400, detail="Invalid id")
        return v
    
    @validator('conference_id')
    def conference_id_must_not_be_empty(cls, v):
        if v is None or v <= 0:
            raise HTTPException(status_code=400, detail="Invalid conference id")
        return v
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid name")
        return v
    
    @validator('start_time')
    def start_time_must_not_be_empty(cls, v):
        if v == "":
            raise HTTPException(status_code=400, detail="Invalid start time")
        return v
    
    @validator('end_time')
    def end_time_must_not_be_empty(cls, v):
        if v == "":
            raise HTTPException(status_code=400, detail="Invalid end time")
        return v
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        if v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid description")
        return v
    
    @validator('date')
    def date_must_not_be_empty(cls, v):
        if v == "":
            raise HTTPException(status_code=400, detail="Invalid date")
        return v
    
    @validator('location')
    def location_must_not_be_empty(cls, v):
        if v == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid location")
        return v
    
    class Config:
        orm_mode = True