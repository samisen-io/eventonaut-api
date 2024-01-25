from pydantic import BaseModel, Field, field_validator, ValidationInfo
from fastapi import HTTPException, status
import logging

class VenuBase(BaseModel):
    name: str
    location: str
    address: str
    geo_location: str | None = None

    @field_validator('name','location','address')
    def check_empty(cls, v: str, info: ValidationInfo):
        if v.strip() == '':
            logging.exception(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} cannot be more than 256 characters")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be more than 256 characters")
        return v
    
    @field_validator('geo_location')
    def check_geo_location(cls, v: str, info: ValidationInfo):
        if v is not None:
            if v == '':
                return None
            elif len(v) > 256:
                logging.exception(f"{info.field_name} cannot be more than 256 characters")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be more than 256 characters")
        return v

class VenueCreate(VenuBase):
    pass

class VenueUpdate(VenuBase):
    id: str
    name: str | None = None
    location: str | None = None
    address: str | None = None

    @field_validator('id')
    def check_id(cls, v: str, info: ValidationInfo):
        if v.strip() == '':
            logging.exception(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} cannot be more than 256 characters")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be more than 256 characters")
        return v

    @field_validator('name','location','address')
    def check_empty(cls, v: str, info: ValidationInfo):
        if v is not None:
            if v.strip() == '':
                return None
            elif len(v) > 256:
                logging.exception(f"{info.field_name} cannot be more than 256 characters")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be more than 256 characters")
        return v
    
class Venue(VenuBase):
    uuid: str = Field(serialization_alias='id')

    class Config:
        orm_mode = True