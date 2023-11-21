from pydantic import BaseModel, validator, Field
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
    conference_logo: str | None = None

    @validator('name')
    def name_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v
    
    @validator('location')
    def location_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid location")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Location too long")
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
        if len(v) > 256:
            raise HTTPException(status_code=400, detail="Description too long")
        return v

class ConferenceUpdate(BaseModel):
    id: str
    name: str | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date  | None = None
    description: str | None = None
    conference_logo: str | None = None

    @validator('id')
    def id_is_not_empty(cls, v):
        if v is None or v == "string" or v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid id")
        return v
    
    @validator('name')
    def name_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid name")
        if len is not None and len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v
    
    @validator('location')
    def location_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid location")
        if len is not None and len(v) > 256:
            raise HTTPException(status_code=400, detail="Location too long")
        return v
    
    @validator('description')
    def description_is_not_empty(cls, v):
        if len(v) > 256:
            raise HTTPException(status_code=400, detail="Description too long")
        return v

#pydantic model for conference
class Conference(ConferenceCreate):
    uuid: str = Field(serialization_alias="id")
    sessions: list[Session] = []
    settings: list[Settings] = []
    class Config:
        orm_mode = True