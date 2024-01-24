from pydantic import BaseModel, Field, field_validator, ValidationInfo
from fastapi import HTTPException, status
from datetime import date
from .settings_schemas import Settings
from .session_schemas import Session
import logging

class ConferenceBase(BaseModel):
    name: str
    location: str
    venue_name: str
    venue_location: str
    start_date: date = Field(..., description="Date format: YYYY-MM-DD")
    end_date: date = Field(..., description="Date format: YYYY-MM-DD")
    description: str | None = None
    conference_logo: str | None = None
    timezone: str | None = None
    registration_link: str | None = None
    conference_banner_url: str | None = None
    information_guide: str

    @field_validator('name','location','venue_name','venue_location','information_guide')
    def value_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} must not be longer than 256 characters")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} must not be longer than 256 characters")
        return v

    @field_validator('description','conference_logo','registration_link','conference_banner_url','timezone')
    def optional_field_validation(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            max_length = 50 if info.field_name == "timezone" else 256
            if len(v) > max_length:
                print(v,"Longest Desc")
                logging.exception(f"{info.field_name} must not be longer than {max_length} characters")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} must not be longer than {max_length} characters")
        return v
    
class ConferenceCreate(ConferenceBase):
    client_id: str | None = None

    @field_validator('client_id')
    def client_id_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
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
        if v.strip() == "":
            logging.exception(f"Invalid {info.field_name}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {info.field_name}")
        return v

    @field_validator('name','client_id','location','venue_name','venue_location','description','conference_logo','registration_link','information_guide','conference_banner_url','timezone')
    def value_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            max_len = 50 if info.field_name == 'timezone' else 256
            if len(v) > max_len:
                logging.exception(f"{info.field_name} cannot be longer than {max_len} characters")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be longer than {max_len} characters")
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
    client_details: ClientDetails | None = None
    
    class Config:
        orm_mode = True