from pydantic import BaseModel, validator
from fastapi import HTTPException
from datetime import date
from .settings_schemas import Settings
from .session_schemas import Session

#pydantic model for conference create
class ConferenceCreate(BaseModel):
    name: str
    location: str
    start_date: date
    end_date: date
    description: str | None = None

    @validator('name')
    def name_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid name")
        return v
    
    @validator('location')
    def location_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid location")
        return v

    @validator('start_date')
    def start_date_is_not_empty(cls, v):
        if v is None:
            raise HTTPException(status_code=400, detail="Invalid start date")
        return v

    @validator('end_date')
    def end_date_is_not_empty(cls, v):
        if v is None:
            raise HTTPException(status_code=400, detail="Invalid end date")
        return v  
    
    @validator('description')
    def description_is_not_empty(cls, v):
        if v == "string":
            raise HTTPException(status_code=400, detail="Invalid description")
        if len is not None and len(v) > 256:
            raise HTTPException(status_code=400, detail="Description should be less than 256 characters")
        return v

class ConferenceUpdate(BaseModel):
    uuid: str
    name: str | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date  | None = None
    description: str | None = None

    @validator('id')
    def id_is_not_empty(cls, v):
        if v is None or v <= 0:
            raise HTTPException(status_code=400, detail="Invalid id")
        return v
    
    @validator('name')
    def name_is_not_empty(cls, v):
        if v == "string" or v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid name")
        return v
    
    @validator('location')
    def location_is_not_empty(cls, v):
        if v == "string" or v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid location")
        return v
    
    @validator('description')
    def description_is_not_empty(cls, v):
        if v == "string" or v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid description")
        if len is not None and len(v) > 256:
            raise HTTPException(status_code=400, detail="Description should be less than 256 characters")
        return v

#pydantic model for conference
class Conference(ConferenceCreate):
    uuid: str
    owner_id: int
    sessions: list[Session] = []
    settings: list[Settings] = []
    class Config:
        orm_mode = True