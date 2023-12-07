from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
from .conference_schemas import Conference
import logging

#pydantic model user base
class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    company: str | None = None
    bussiness_type: str
    timezone: str | None = None

    @validator('email')
    def email_is_valid(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" "):
            logging.exception("Invalid email")
            raise HTTPException(status_code=400, detail="Invalid email")
        elif len(v) > 256:
            logging.exception("Email too long")
            raise HTTPException(status_code=400, detail="Email too long")
        return v

    @validator('first_name')
    def first_name_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            logging.exception("Invalid first name")
            raise HTTPException(status_code=400, detail="Invalid first name")
        elif len(v) > 256:
            logging.exception("First name too long")
            raise HTTPException(status_code=400, detail="First name too long")
        return v
    
    @validator('last_name')
    def last_name_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            logging.exception("Invalid last name")
            raise HTTPException(status_code=400, detail="Invalid last name")
        elif len(v) > 256:
            logging.exception("Last name too long")
            raise HTTPException(status_code=400, detail="Last name too long")
        return v
    
    @validator('company')
    def company_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                logging.exception("Invalid company")
                raise HTTPException(status_code=400, detail="Invalid company")
            elif len(v) > 256:
                logging.exception("Company too long")
                raise HTTPException(status_code=400, detail="Company too long")
        return v

    @validator('bussiness_type')
    def bussiness_type_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            logging.exception("Invalid bussiness type")
            raise HTTPException(status_code=400, detail="Invalid bussiness type")
        elif len(v) > 256:
            logging.exception("Bussiness type too long")
            raise HTTPException(status_code=400, detail="Bussiness type too long")
        return v
    
    @validator('timezone')
    def timezone_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                logging.exception("Invalid timezone")
                raise HTTPException(status_code=400, detail="Invalid timezone")
            elif len(v) > 50:
                logging.exception("Timezone too long")
                raise HTTPException(status_code=400, detail="Timezone too long")
        return v
    
class UserBaseUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    company: str |None = None
    bussiness_type: str |None = None
    timezone: str |None = None

    @validator('first_name')
    def first_name_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            logging.exception("Invalid first name")
            raise HTTPException(status_code=400, detail="Invalid first name")
        elif len(v) > 256:
            logging.exception("First name too long")
            raise HTTPException(status_code=400, detail="First name too long")
        return v
    
    @validator('last_name')
    def last_name_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            logging.exception("Invalid last name")
            raise HTTPException(status_code=400, detail="Invalid last name")
        elif len(v) > 256:
            logging.exception("Last name too long")
            raise HTTPException(status_code=400, detail="Last name too long")
        return v
    
    @validator('company')
    def company_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            logging.exception("Invalid company")
            raise HTTPException(status_code=400, detail="Invalid company")
        elif len(v) > 256:
            logging.exception("Company too long")
            raise HTTPException(status_code=400, detail="Company too long")
        return v

    @validator('bussiness_type')
    def bussiness_type_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            logging.exception("Invalid bussiness type")
            raise HTTPException(status_code=400, detail="Invalid bussiness type")
        elif len(v) > 256:
            logging.exception("Bussiness type too long")
            raise HTTPException(status_code=400, detail="Bussiness type too long")
        return v
    
    @validator('timezone')
    def timezone_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):    
            logging.exception("Invalid timezone")
            raise HTTPException(status_code=400, detail="Invalid timezone")
        elif len(v) > 50:
            logging.exception("Timezone too long")
            raise HTTPException(status_code=400, detail="Timezone too long")
        return v

#pydantic model for user create
class UserCreate(UserBase):
    hashed_password: str

    @validator('hashed_password')
    def hashed_password_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" "):
            logging.exception("Invalid password")
            raise HTTPException(status_code=400, detail="Invalid password")
        elif len(v) < 8:
            logging.exception("Password too short")
            raise HTTPException(status_code=400, detail="Password too short")
        elif len(v) > 16:
            logging.exception("Password too long")
            raise HTTPException(status_code=400, detail="Password too long")
        return v

#pydantic model for user password
class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

    @validator('old_password')
    def old_password_validator(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" "):
            logging.exception("Invalid old password")
            raise HTTPException(status_code=400, detail="Invalid old password")
        if len(v) < 8:
            logging.exception("Old password too short")
            raise HTTPException(status_code=400, detail="Old password too short")
        elif len(v) > 16:
            logging.exception("Old password too long")
            raise HTTPException(status_code=400, detail="Old password too long")
        return v

    @validator('new_password')
    def new_password_validator(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" "):
            logging.exception("Invalid new password")
            raise HTTPException(status_code=400, detail="Invalid new password")
        if len(v) < 8:
            logging.exception("New password too short")
            raise HTTPException(status_code=400, detail="New password too short")
        elif len(v) > 16:
            logging.exception("New password too long")
            raise HTTPException(status_code=400, detail="New password too long")
        return v

#pydantic model for user
class User(UserBase):
    uuid: str = Field(serialization_alias="id")
    conferences: list[Conference] = []
    is_active: bool
    class Config:
        orm_mode = True
        
class UserAuthentication(User):
    role: str
        