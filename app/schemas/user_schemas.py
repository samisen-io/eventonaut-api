from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
from .conference_schemas import Conference

#pydantic model user base
class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    company: str | None = None
    bussiness_type: str

    @validator('email')
    def email_is_valid(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" "):
            raise HTTPException(status_code=400, detail="Invalid email")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Email too long")
        return v

    @validator('first_name')
    def first_name_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid first name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="First name too long")
        return v
    
    @validator('last_name')
    def last_name_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid last name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Last name too long")
        return v
    
    
    @validator('bussiness_type')
    def bussiness_type_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid bussiness type")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Bussiness type too long")
        return v

class UserBaseUpdate(BaseModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    company: str |None = None
    bussiness_type: str |None = None
    
    @validator('email')
    def email_is_valid(cls, v):
        if v is not None and (v.strip() == "" or v == "string" or v.__contains__(" ")):
            raise HTTPException(status_code=400, detail="Invalid email")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Email too long")
        return v

    @validator('first_name')
    def first_name_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid first name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="First name too long")
        return v
    
    @validator('last_name')
    def last_name_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid last name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Last name too long")
        return v
    
    @validator('bussiness_type')
    def bussiness_type_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid bussiness type")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Bussiness type too long")
        return v

#pydantic model for user create
class UserCreate(UserBase):
    hashed_password: str

    @validator('hashed_password')
    def hashed_password_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" "):
            raise HTTPException(status_code=400, detail="Invalid password")
        elif len(v) < 8:
            raise HTTPException(status_code=400, detail="Password too short")
        elif len(v) > 16:
            raise HTTPException(status_code=400, detail="Password too long")
        return v

#pydantic model for user password
class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

    @validator('old_password')
    def old_password_validator(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" "):
            raise HTTPException(status_code=400, detail="Invalid old password")
        if len(v) < 8:
            raise HTTPException(status_code=400, detail="Old password too short")
        elif len(v) > 16:
            raise HTTPException(status_code=400, detail="Old password too long")
        return v

    @validator('new_password')
    def new_password_validator(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" "):
            raise HTTPException(status_code=400, detail="Invalid new password")
        if len(v) < 8:
            raise HTTPException(status_code=400, detail="New password too short")
        elif len(v) > 16:
            raise HTTPException(status_code=400, detail="New password too long")
        return v

#pydantic model for user
class User(UserBase):
    uuid: str = Field(serialization_alias="id")
    conferences: list[Conference] = []
    is_active: bool
    class Config:
        orm_mode = True
