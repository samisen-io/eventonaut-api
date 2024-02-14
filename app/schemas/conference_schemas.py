from pydantic import BaseModel, Field, field_validator, ValidationInfo
from datetime import date
from ..schemas import venue_schemas, client_schemas, sponsor_schemas
import logging
from ..static_enums import event
from ..url_validator import check_url

class ConferenceBase(BaseModel):
    name: str
    location: str
    start_date: date = Field(..., description="Date format: YYYY-MM-DD")
    end_date: date = Field(..., description="Date format: YYYY-MM-DD")
    description: str | None = None
    conference_logo: str | None = None
    timezone: str | None = None
    registration_link: str | None = None
    conference_banner_url: str | None = None
    information_guide: str
    status: str 

    @field_validator('name','location','information_guide')
    def value_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} must not be longer than 256 characters")
            raise ValueError(f"{info.field_name} must not be longer than 256 characters")
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
                raise ValueError(f"{info.field_name} must not be longer than {max_length} characters")
        return v
    
    @field_validator("status")
    def check_status(cls, v):
        v = v.upper()
        if v not in list(event.EventEnum.__members__):
            raise ValueError("Invalid status")
        return v
    
    @field_validator('information_guide', 'conference_banner_url', 'registration_link', 'conference_logo')
    def validate_url(cls, v, info: ValidationInfo):
        if v is not None:
            if not check_url(v):
                raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v
    
class ConferenceCreate(ConferenceBase):
    client_id: str | None = None
    venue_id: str
    sponsor_ids: list[str] | None = None

    @field_validator('venue_id')
    def venue_id_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        return v

    @field_validator('client_id')
    def client_id_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
        return v
    
    @field_validator('sponsor_ids')
    def sponsor_ids_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if len(v) == 0:
                return None
            for sponsor_id in v:
                if sponsor_id.strip() == "":
                    logging.exception(f"{info.field_name} cannot be empty")
                    raise ValueError(f"{info.field_name} cannot be empty")
                elif len(sponsor_id) > 256:
                    logging.exception(f"{info.field_name} must not be longer than 256 characters")
                    raise ValueError(f"{info.field_name} must not be longer than 256 characters")
        return v

class ConferenceUpdate(BaseModel):
    id: str
    client_id: str | None = None
    venue_id: str | None = None
    sponsor_ids: list[str] | None = None
    name: str | None = None
    location: str | None = None
    start_date: date | None = Field(default=None, description="Date format: YYYY-MM-DD")
    end_date: date | None = Field(default=None, description="Date format: YYYY-MM-DD")
    description: str | None = None
    conference_logo: str | None = None
    timezone: str | None = None
    registration_link: str | None = None
    conference_banner_url: str | None = None
    information_guide: str | None = None
    status: str | None = None

    @field_validator('id')
    def id_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"Invalid {info.field_name}")
            raise ValueError(f"Invalid {info.field_name}")
        return v

    @field_validator('name','client_id','location','description','venue_id','conference_logo','registration_link','information_guide','conference_banner_url','timezone')
    def value_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            max_len = 50 if info.field_name == 'timezone' else 256
            if len(v) > max_len:
                logging.exception(f"{info.field_name} cannot be longer than {max_len} characters")
                raise ValueError(f"{info.field_name} cannot be longer than {max_len} characters")
        return v
    
    @field_validator('timezone')
    def timezone_is_valid(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 50:
                logging.exception(f"{info.field_name} must not be longer than 50 characters")
                raise ValueError(f"{info.field_name} must not be longer than 50 characters")
        return v
    
    @field_validator('sponsor_ids')
    def sponsor_ids_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if len(v) == 0:
                return None
            for sponsor_id in v:
                if sponsor_id.strip() == "":
                    logging.exception(f"{info.field_name} cannot be empty")
                    raise ValueError(f"{info.field_name} cannot be empty")
                elif len(sponsor_id) > 256:
                    logging.exception(f"{info.field_name} must not be longer than 256 characters")
                    raise ValueError(f"{info.field_name} must not be longer than 256 characters")
        return v
    
    @field_validator("status")
    def check_status(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            v = v.upper()
            if v not in list(event.EventEnum.__members__):
                raise ValueError("Invalid status")
        return v
    
    @field_validator('information_guide', 'conference_banner_url', 'registration_link', 'conference_logo')
    def validate_url(cls, v, info: ValidationInfo):
        if v is not None:
            if not check_url(v):
                raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v

#pydantic model for conference
class Conference(ConferenceBase):
    uuid: str = Field(serialization_alias="id")
    client_details: client_schemas.Client | None
    venue_details: venue_schemas.Venue
    sponsor_details: list[sponsor_schemas.Sponsor] | None
    
    class Config:
        orm_mode = True

class ConferenceListSummary(BaseModel):
    no_of_events: int
    first_event_start_date: date
    last_event_end_date: date
    no_of_sponsors: int
    no_of_clients: int
    number_of_attendees: int