from pydantic import BaseModel, Field, field_validator, ValidationInfo
import logging
from ..url_validator import check_url

class ExhibitorBase(BaseModel):
    name: str
    address: str
    about: str
    contact_name: str
    contact_phone: str
    contact_email: str
    booth_number: str
    category: str
    exhibitor_logo: str | None = None
    exhibitor_banner: str | None = None
    
    @field_validator('name', 'address', 'about', 'contact_name', 'contact_email', 'booth_number', 'category')
    def check_empty(cls, v, info: ValidationInfo):
        if v == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} cannot be more than 256 characters")
            raise ValueError(f"{info.field_name} cannot be more than 256 characters")
        return v
    
    @field_validator('contact_phone')
    def check_booth_number(cls, v, info: ValidationInfo):
        if v == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        elif not 10 <= len(v) <= 15:
            logging.exception(f"Invalid {info.field_name}")
            raise ValueError(f"Invalid {info.field_name}")
        return v
    
    @field_validator('exhibitor_logo', 'exhibitor_banner')
    def check_url(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                logging.exception(f"{info.field_name} cannot be more than 256 characters")
                raise ValueError(f"{info.field_name} cannot be more than 256 characters")
            if not check_url(v):
                logging.exception(f"Broken {info.field_name} link or invalid url")
                raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v
    
class ExhibitorCreate(ExhibitorBase):
    conference_id: str
    
    @field_validator('conference_id')
    def check_empty(cls, v, info: ValidationInfo):
        if v == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} cannot be more than 256 characters")
            raise ValueError(f"{info.field_name} cannot be more than 256 characters")
        return v

class ExhibitorUpdate(BaseModel):
    id: str
    conference_id: str | None = None
    name: str | None = None
    address: str | None = None
    about: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    booth_number: str | None = None
    category: str | None = None
    exhibitor_logo: str | None = None
    exhibitor_banner: str | None = None
    
    @field_validator('id')
    def check_id(cls, v, info: ValidationInfo):
        if v == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} cannot be more than 256 characters")
            raise ValueError(f"{info.field_name} cannot be more than 256 characters")
        return v
    
    @field_validator('conference_id', 'name', 'address', 'about', 'contact_name', 'contact_email', 'booth_number', 'category', 'exhibitor_logo', 'exhibitor_banner')
    def check_none(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                logging.exception(f"{info.field_name} cannot be more than 256 characters")
                raise ValueError(f"{info.field_name} cannot be more than 256 characters")
        return v
    
    @field_validator('contact_phone')
    def check_phone(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            if not 10 <= len(v) <= 15:
                logging.exception(f"Invalid {info.field_name}")
                raise ValueError(f"Invalid {info.field_name}")
        return v
    
    @field_validator('exhibitor_logo', 'exhibitor_banner')
    def check_url(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                logging.exception(f"{info.field_name} cannot be more than 256 characters")
                raise ValueError(f"{info.field_name} cannot be more than 256 characters")
            if not check_url(v):
                logging.exception(f"Broken {info.field_name} link or invalid url")
                raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v
    
class ExhibitorResponse(BaseModel):
    uuid: str = Field(serialization_alias='id')
    conference_uuid: str = Field(serialization_alias='conference_id')
    name: str
    address: str
    about: str
    contact_name: str
    contact_phone: str
    contact_email: str
    booth_number: str
    category: str
    exhibitor_logo: str | None = None
    exhibitor_banner: str | None = None

    class Config:
        orm_mode = True