from pydantic import BaseModel, validator, Field, field_validator, ValidationInfo
from fastapi import HTTPException, status
import logging
from ..url_validator import check_url

class SpeakerBase(BaseModel):
    name: str
    email: str
    title: str
    bio: str
    profile_image_url: str | None = None

    @field_validator('name','email','title','bio')
    def validate_fields(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be empty")
        max_length = 2048 if info.field_name == "bio" else 256
        if len(v) > max_length:
            raise HTTPException(status_code=400, detail=f"{info.field_name} must be less than {max_length} characters")
        return v
    
    @field_validator('profile_image_url')
    def validate_profile_image_url(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile image url too long")
            if not check_url(v):
                raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v

class SpeakerCreate(SpeakerBase):
    pass

class SpeakerUpdate(BaseModel):
    id: str
    name: str | None = None
    title: str | None = None
    bio: str | None = None
    profile_image_url: str | None = None

    @validator('id')
    def validate_id(cls, v):
        if v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid id")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Id too long")
        return v

    @field_validator('name','title','bio','profile_image_url')
    def validate_update(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            max_length = 2048 if info.field_name == "bio" else 256
            if len(v) > max_length:
                raise HTTPException(status_code=400, detail=f"{info.field_name} must be less than {max_length} characters")
        return v
    
    @field_validator('profile_image_url')
    def validate_profile_image_url(cls, v, info: ValidationInfo):
        if v is not None:
            if not check_url(v):
                raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v

class Speaker(SpeakerBase):
    uuid: str = Field(serialization_alias="id")

    class Config:
        orm_mode = True