from pydantic import BaseModel, Field, field_validator, ValidationInfo
from fastapi import HTTPException, status as statuscode
import logging

class OrganizationBase(BaseModel):
    name: str
    business_type: str | None = None
    description: str | None = None
    address: str | None = None
    logo_image_url: str | None = None
    website_url: str | None = None

    @field_validator('name')
    @classmethod
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} should be less than 256 characters")
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} should be less than 256 characters")
        return v

    @field_validator('business_type', 'description', 'address', 'logo_image_url', 'website_url')
    @classmethod
    def optional_field_validation(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            if len(v) > 256:
                logging.exception(f"{info.field_name} should be less than 256 characters")
                raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} should be less than 256 characters")
        return v

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    id: str
    name: str | None = None
    business_type: str | None = None
    description: str | None = None
    address: str | None = None
    logo_image_url: str | None = None
    website_url: str | None = None

    @field_validator('name', 'business_type', 'description', 'address', 'logo_image_url', 'website_url')
    @classmethod
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            if len(v) > 256:
                logging.exception(f"{info.field_name} should be less than 256 characters")
                raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} should be less than 256 characters")
        return v

class Organization(OrganizationBase):
    uuid: str = Field(serialization_alias='id')

    class Config:
        orm_mode = True