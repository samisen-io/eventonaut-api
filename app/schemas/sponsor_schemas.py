from pydantic import BaseModel, Field, field_validator, field_serializer, ValidationInfo
from fastapi import HTTPException, status
import logging

class SponsorBase(BaseModel):
    email: str
    name: str
    description: str
    contact_name: str
    contact_phone: int
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
    def check_phone_number(cls, v, info: ValidationInfo):
        if len(str(v)) != 10:
            logging.info(f"Invalid {info.field_name}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {info.field_name}")
        return v

class SponsorCreate(SponsorBase):
    conference_id: str

    @field_validator('conference_id')
    def check_conference_id(cls, v, info: ValidationInfo):
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

class SponsorUpdate(BaseModel):
    id: str
    conference_id: str | None = None
    name: str | None = None
    description: str | None = None
    contact_name: str | None = None
    contact_phone: int | None = None
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
    def check_phone_number(cls, v, info: ValidationInfo):
        if v is not None and len(str(v)) != 10:
            logging.info(f"Invalid {info.field_name}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {info.field_name}")
        return v
        
    @field_validator('conference_id','name','description','contact_name','logo_image_url','sponsorship_level')
    def check_empty_string(cls, v, info: ValidationInfo):
        if v is not None:
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
            
class Sponsor(SponsorBase):
    uuid: str = Field(serialization_alias='id')

    class Config:
        orm_mode = True