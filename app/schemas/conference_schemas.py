from pydantic import BaseModel, Field, field_validator, ValidationInfo
from fastapi import HTTPException
from datetime import date
from .settings_schemas import Settings
from .session_schemas import Session
from typing import Optional, Any
import logging

class ConferenceBase(BaseModel):
    name: str
    location: str
    venue_name: str = "None"
    venue_location: str = "None"
    start_date: date = Field(..., description="Date format: YYYY-MM-DD")
    end_date: date = Field(..., description="Date format: YYYY-MM-DD")
    description: str = "None"
    conference_logo: str = "None"
    timezone: str = "None"
    registration_link: str = "None"
    conference_banner_url: str = "None"
    information_guide: str

    @field_validator('name','location','venue_name','venue_location','information_guide','description','conference_logo','registration_link','conference_banner_url')
    def value_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=400, detail=f"{info.field_name} cannot be empty")
        elif v == "string":
            logging.exception(f"Invalid {info.field_name}")
            raise HTTPException(status_code=400, detail=f"Invalid {info.field_name}")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} must not be longer than 256 characters")
            raise HTTPException(status_code=400, detail=f"{info.field_name} must not be longer than 256 characters")
        return v
    
    @field_validator('timezone')
    def timezone_is_valid(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=400, detail=f"{info.field_name} cannot be empty")
        elif v == "string":
            logging.exception(f"Invalid {info.field_name}")
            raise HTTPException(status_code=400, detail=f"Invalid {info.field_name}")
        elif len(v) > 50:
            logging.exception(f"{info.field_name} must not be longer than 50 characters")
            raise HTTPException(status_code=400, detail=f"{info.field_name} must not be longer than 50 characters")
        return v

#pydantic model for conference create
class ConferenceCreate(ConferenceBase):
    client_id: str | None = None

    @field_validator('client_id')
    def client_id_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                raise HTTPException(status_code=400, detail="Invalid client id")
            if len(v) > 256:
                raise HTTPException(status_code=400, detail="Client id too long")
        return v

class ConferenceUpdate(BaseModel):
    id: str
    client_id: str | None = None
    name: str | None = None
    location: str | None = None
    venue_name: str | None = None
    venue_location: str | None = None
    start_date: date | None = Field(default=None, description="Date format: YYYY-MM-DD")
    end_date: date | None = Field(default=None, description="Date format: YYYY-MM-DD")
    description: str | None = None
    conference_logo: str | None = None
    timezone: str | None = None
    registration_link: str | None = None
    conference_banner_url: str | None = None
    information_guide: str | None = None

    @field_validator('id')
    def id_is_not_empty(cls, v, info: ValidationInfo):
        if v == "string" or v.strip() == "":
            logging.exception(f"Invalid {info.field_name}")
            raise HTTPException(status_code=400, detail=f"Invalid {info.field_name}")
        return v

    @field_validator('name','client_id','location','venue_name','venue_location','description','conference_logo','registration_link','information_guide','conference_banner_url')
    def value_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                logging.exception(f"{info.field_name} cannot be empty")
                raise HTTPException(status_code=400, detail=f"{info.field_name} cannot be empty")
            if v == "string":
                logging.exception(f"Invalid {info.field_name}")
                raise HTTPException(status_code=400, detail=f"Invalid {info.field_name}")
            if len(v) > 256:
                logging.exception(f"{info.field_name} cannot be longer than 256 characters")
                raise HTTPException(status_code=400, detail=f"{info.field_name} cannot be longer than 256 characters")
        return v
    
    @field_validator('timezone')
    def timezone_is_valid(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                logging.exception(f"{info.field_name} cannot be empty")
                raise HTTPException(status_code=400, detail=f"{info.field_name} cannot be empty")
            elif v == "string":
                logging.exception(f"Invalid {info.field_name}")
                raise HTTPException(status_code=400, detail=f"Invalid {info.field_name}")
            elif len(v) > 50:
                logging.exception(f"{info.field_name} must not be longer than 50 characters")
                raise HTTPException(status_code=400, detail=f"{info.field_name} must not be longer than 50 characters")
        return v

class ClientDetails(BaseModel):
    id: str
    name: str

#pydantic model for conference
class Conference(ConferenceBase):
    uuid: str = Field(serialization_alias="id")
    client_details: ClientDetails | None
    sessions: list[Session] = []
    settings: list[Settings] = []
    
    class Config:
        orm_mode = True