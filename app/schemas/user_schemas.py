from typing import List
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from fastapi import HTTPException, status as statuscode
import logging
from ..static_enums import organizer

class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    company: str | None = None
    business_type: str
    timezone: str | None = None
    status: str
    profile_image_url: str | None = None
    list_of_roles: List[str] = []

    @field_validator('email','first_name','last_name','business_type')
    @classmethod
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} should be less than 256 characters")
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} should be less than 256 characters")
        return v
    
    @field_validator("status")
    @classmethod
    def check_status(cls, v):
        v = v.upper()
        if v not in list(organizer.OrganizerEnum.__members__):
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail="Invalid status")
        return v
    
    @field_validator('company','timezone','profile_image_url')
    @classmethod
    def optional_field_validation(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            max_len = 50 if info.field_name == "timezone" else 256
            if len(v) > max_len:
                logging.exception(f"{info.field_name} should be less than {max_len} characters")
                raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} should be less than {max_len} characters")
        return v
    
class UserBaseUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    company: str |None = None
    business_type: str |None = None
    timezone: str |None = None
    status: str |None = None
    profile_image_url: str |None = None
    list_of_roles: List[str] | None = None

    @field_validator('first_name','last_name','company','business_type','timezone','profile_image_url')
    @classmethod
    def user_is_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            max_len = 50 if info.field_name == "timezone" else 256
            if len(v) > max_len:
                logging.exception(f"{info.field_name} should be less than {max_len} characters")
                raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} should be less than {max_len} characters")
        return v
    
    @field_validator("status")
    @classmethod
    def check_status(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            v = v.upper()
            if v not in list(organizer.OrganizerEnum.__members__):
                raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail="Invalid status")
        return v

class UserCreate(UserBase):
    hashed_password: str
    
    @field_validator('hashed_password')
    @classmethod
    def hashed_password_is_not_empty(cls, v):
        if v.strip() == "" or v.__contains__(" "):
            logging.exception("Invalid password")
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail="Invalid password")
        if not 8 <= len(v) <= 16:
            logging.exception("Password should be between 8 and 16 characters")
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail="Password should be between 8 and 16 characters")
        return v

class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

    @field_validator('old_password','new_password')
    @classmethod
    def password_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "" or v.__contains__(" "):
            logging.exception(f"Invalid {info.field_name}")
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail=f"Invalid {info.field_name}")
        if not 8 <= len(v) <= 16:
            logging.exception(f"{info.field_name} should be between 8 and 16 characters")
            raise HTTPException(status_code=statuscode.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} should be between 8 and 16 characters")
        return v

class User(UserBase):
    uuid: str = Field(serialization_alias="id")
    is_active: bool
    
    class Config:
        orm_mode = True
        
class UserAuthentication(User):
    role: str