from pydantic import BaseModel, field_validator, validator, Field, ValidationInfo
from fastapi import HTTPException, status
from ..static_enums import client
import logging

class ClientBase(BaseModel):
    name: str
    contact_name: str
    contact_email: str
    contact_phone: str
    address: str
    profile_image_url: str | None = None
    status: str

    @field_validator('name','contact_name','contact_email','address')
    def check_empty(cls, v: str, info: ValidationInfo):
        if v.strip() == '':
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} cannot be more than 256 characters")
            raise ValueError(f"{info.field_name} cannot be more than 256 characters")
        return v
    
    @field_validator('contact_phone')
    def contact_phone_is_not_empty(cls, v):
        if v.strip() == "":
            logging.exception(f"Phone number cannot be empty")
            raise ValueError(f"Phone number cannot be empty")
        elif not 10 <= len(v) <= 15:
            logging.exception(f"Invalid Phone Number")
            raise ValueError(f"Invalid Phone Number")
        return v
    
    @field_validator('profile_image_url')
    def profile_image_url_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                logging.exception(f"Profile image url too long")
                raise ValueError(f"Profile image url too long")
        return v
    
    @field_validator("status")
    def check_status(cls, v):
        v = v.upper()
        if v not in list(client.ClientEnum.__members__):
            logging.exception("Invalid status")
            raise ValueError("Invalid status")
        return v

class ClientUpdate(BaseModel):
    id: str
    name: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    status: str | None = None
    address: str | None = None
    profile_image_url: str | None = None

    @field_validator('id')
    def id_is_not_empty(cls, v, info: ValidationInfo):
        if v == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} cannot be longer than 256 characters")
            raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v
    
    @field_validator('contact_email', 'contact_name', 'name', 'address', 'profile_image_url')
    def check_empty_string(cls, v, info: ValidationInfo):
        if v is not None:
            if v == "":
                return None
            if len(v) > 256:
                logging.exception(f"{info.field_name} cannot be longer than 256 characters")
                raise ValueError(f"{info.field_name} cannot be longer than 256 characters")
        return v
    
    @field_validator('contact_phone')
    def contact_phone_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            elif not 10 <= len(v) <= 15:
                logging.exception(f"Invalid Phone Number")
                raise ValueError(f"Invalid Phone Number")
        return v
    
    @field_validator("status")
    def check_status(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            v = v.upper()
            if v not in list(client.ClientEnum.__members__):
                logging.exception("Invalid status")
                raise ValueError("Invalid status")
        return v

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    uuid: str = Field(serialization_alias="id")

    class Config:
        orm_mode = True