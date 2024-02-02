from pydantic import BaseModel, Field, field_validator, ValidationInfo
from fastapi import HTTPException, status
import logging

class SponsorBase(BaseModel):
    email: str
    name: str
    description: str
    contact_name: str
    contact_phone: str
    logo_image_url: str
    sponsorship_level: str

    @field_validator('email','name','description','contact_name','logo_image_url','sponsorship_level')
    def check_empty_string(cls, v, info: ValidationInfo):
        if v == "":
            logging.info(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be empty")
        elif v == 'string':
            logging.info(f"Invalid {info.field_name}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {info.field_name}")
        elif len(v) > 256:
            logging.info(f"{info.field_name} cannot be longer than 256 characters")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be longer than 256 characters")
        return v

    @field_validator('contact_phone')
    def check_phone_number(cls, v: str, info: ValidationInfo):
        if len(v) != 10 or not v.isdigit():
            logging.info(f"Invalid {info.field_name}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {info.field_name}")
        return v

class SponsorCreate(SponsorBase):
    pass

class SponsorUpdate(BaseModel):
    id: str
    name: str | None = None
    description: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    logo_image_url: str | None = None
    sponsorship_level: str | None = None

    @field_validator('id')
    def check_id(cls, v, info: ValidationInfo):
        if v == "":
            logging.info(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be empty")
        elif v == 'string':
            logging.info(f"Invalid {info.field_name}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {info.field_name}")
        elif len(v) > 256:
            logging.info(f"{info.field_name} cannot be longer than 256 characters")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be longer than 256 characters")
        return v
        
    @field_validator('contact_phone')
    def check_phone_number(cls, v: str, info: ValidationInfo):
        if v is not None:
            if len(v) != 10 or not v.isdigit():
                logging.info(f"Invalid {info.field_name}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {info.field_name}")
        return v
        
    @field_validator('name','description','contact_name','logo_image_url','sponsorship_level')
    def check_empty_string(cls, v, info: ValidationInfo):
        if v is not None:
            if v == "":
                return None
            elif v == 'string':
                logging.info(f"Invalid {info.field_name}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {info.field_name}")
            elif len(v) > 256:
                logging.info(f"{info.field_name} cannot be longer than 256 characters")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be longer than 256 characters")
        return v
            
class Sponsor(SponsorBase):
    uuid: str = Field(serialization_alias='id')

    class Config:
        orm_mode = True