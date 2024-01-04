from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
from datetime import date
from .settings_schemas import Settings
from .session_schemas import Session
from typing import Optional, Any
import logging

#pydantic model for conference create
class ConferenceCreate(BaseModel):
    name: str
    client_id: str | None = None
    location: str
    start_date: date
    end_date: date
    description: str | None = "None"
    conference_logo: str | None = "None"
    timezone: str | None = "None"
    registration_link: str | None = "None"
    conference_banner_url: str | None = "None"
    information_guide: str

    @validator('name')
    def name_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            logging.exception("Invalid name")
            raise HTTPException(status_code=400, detail="Invalid name")
        elif len(v) > 256:
            logging.exception("Name too long")
            raise HTTPException(status_code=400, detail="Name too long")
        return v
    
    @validator('client_id')
    def client_id_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                raise HTTPException(status_code=400, detail="Invalid client id")
            if len(v) > 256:
                raise HTTPException(status_code=400, detail="Client id too long")
        return v
    
    @validator('location')
    def location_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            logging.exception("Invalid location")
            raise HTTPException(status_code=400, detail="Invalid location")
        elif len(v) > 256:
            logging.exception("Location too long")
            raise HTTPException(status_code=400, detail="Location too long")
        return v

    @validator('start_date')
    def start_date_is_not_empty(cls, v):
        if v is None:
            logging.exception("Invalid start date")
            raise HTTPException(status_code=400, detail="Invalid start date")
        return v

    @validator('end_date')
    def end_date_is_not_empty(cls, v):
        if v is None:
            logging.exception("Invalid end date")
            raise HTTPException(status_code=400, detail="Invalid end date")
        return v  

    @validator('description')
    def description_is_not_empty(cls, v):
        if len(v) > 256:
            logging.exception("Description too long")
            raise HTTPException(status_code=400, detail="Description too long")
        return v
    
    @validator('timezone')
    def timezone_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            logging.exception("Invalid timezone")
            raise HTTPException(status_code=400, detail="Invalid timezone")
        elif len(v) > 50:
            logging.exception("Timezone too long")
            raise HTTPException(status_code=400, detail="Timezone too long")
        return v
    
    @validator('registration_link')
    def registration_link_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            logging.exception("Invalid registration link")
            raise HTTPException(status_code=400, detail="Invalid registration link")
        elif len(v) > 256:
            logging.exception("Registration link too long")
            raise HTTPException(status_code=400, detail="Registration link too long")
        return v
    
    @validator('information_guide')
    def information_guide_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid information guide")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Information guide too long")
        return v
    
    @validator('conference_banner_url')
    def conference_banner_url_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid conference banner url")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Conference banner url too long")
        return v

class ConferenceUpdate(BaseModel):
    id: str
    name: str | None = None
    client_id: str | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date  | None = None
    description: str | None = None
    conference_logo: str | None = None
    timezone: str | None = None
    registration_link: str | None = None
    information_guide: str | None = None
    conference_banner_url: str | None = None

    @validator('id')
    def id_is_not_empty(cls, v):
        if v is None or v == "string" or v.strip() == "":
            logging.exception("Invalid id")
            raise HTTPException(status_code=400, detail="Invalid id")
        return v
    
    @validator('name')
    def name_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                logging.exception("Invalid name")
                raise HTTPException(status_code=400, detail="Invalid name")
            if len(v) > 256:
                logging.exception("Name too long")
                raise HTTPException(status_code=400, detail="Name too long")
        return v
    
    @validator('client_id')
    def client_id_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                raise HTTPException(status_code=400, detail="Invalid client id")
            if len(v) > 256:
                raise HTTPException(status_code=400, detail="Client id too long")
        return v
    
    @validator('location')
    def location_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                logging.exception("Invalid location")
                raise HTTPException(status_code=400, detail="Invalid location")
            if len(v) > 256:
                logging.exception("Location too long")
                raise HTTPException(status_code=400, detail="Location too long")
        return v
    
    @validator('description')
    def description_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                raise HTTPException(status_code=400, detail="Invalid description")
            if len(v) > 256:
                logging.exception("Description too long")
                raise HTTPException(status_code=400, detail="Description too long")
        return v
    
    @validator('timezone')
    def timezone_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                logging.exception("Invalid timezone")
                raise HTTPException(status_code=400, detail="Invalid timezone")
            if len(v) > 256:
                logging.exception("Timezone too long")
                raise HTTPException(status_code=400, detail="Timezone too long")
        return v
    
    @validator('registration_link')
    def registration_link_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                logging.exception("Invalid registration link")
                raise HTTPException(status_code=400, detail="Invalid registration link")
            if len(v) > 256:
                logging.exception("Registration link too long")
                raise HTTPException(status_code=400, detail="Registration link too long")
        return v
    
    @validator('information_guide')
    def information_guide_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                raise HTTPException(status_code=400, detail="Invalid information guide")
            if len(v) > 256:
                raise HTTPException(status_code=400, detail="Information guide too long")
        return v
    
    @validator('conference_banner_url')
    def conference_banner_url_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid conference banner url")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Conference banner url too long")
        return v

#pydantic model for conference
class Conference(BaseModel):
    uuid: str = Field(serialization_alias="id")
    name: str
    location: str
    start_date: date
    end_date: date
    description: str | None = "None"
    conference_logo: str | None = "None"
    timezone: str | None = "None"
    registration_link: str | None = "None"
    conference_banner_url: str | None = "None"
    information_guide: str
    sessions: list[Session] = []
    settings: list[Settings] = []
    class Config:
        orm_mode = True

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
    
    @validator('timezone')
    def timezone_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid timezone")
        elif len(v) > 50:
            raise HTTPException(status_code=400, detail="Timezone too long")
        return v
    
    @validator('registration_link')
    def registration_link_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid registration link")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Registration link too long")
        return v
    
    @validator('information_guide')
    def information_guide_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid information guide")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Information guide too long")
        return v
    
    @validator('conference_banner_url')
    def conference_banner_url_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid conference banner url")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Conference banner url too long")
        return v