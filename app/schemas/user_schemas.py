from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
from .conference_schemas import Conference

#pydantic model user base
class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    account_type: str
    bussiness_type: str

    @validator('first_name')
    def first_name_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid first name")
        return v
    
    @validator('last_name')
    def last_name_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid last name")
        return v
    
    @validator('account_type')
    def account_type_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string" or (v.upper() != "INDIVIDUAL" and v.upper() != "COMPANY"):
            raise HTTPException(status_code=400, detail="Invalid account type")
        return v
    
    @validator('bussiness_type')
    def bussiness_type_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid bussiness type")
        return v

class UserBaseUpdate(BaseModel):
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    account_type: str |None = None
    bussiness_type: str |None = None
    
    @validator('first_name')
    def first_name_is_not_empty(cls, v):
        if v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid first name")
        return v
    
    @validator('last_name')
    def last_name_is_not_empty(cls, v):
        if v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid last name")
        return v
    
    @validator('account_type')
    def account_type_is_not_empty(cls, v):
        if v.strip() == "" or v == "string" or (v.upper() != "INDIVIDUAL" and v.upper() != "COMPANY"):
            raise HTTPException(status_code=400, detail="Invalid account type")
        return v
    
    @validator('bussiness_type')
    def bussiness_type_is_not_empty(cls, v):
        if v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid bussiness type")
        return v

#pydantic model for user create
class UserCreate(UserBase):
    hashed_password: str

    @validator('hashed_password')
    def hashed_password_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" "):
            raise HTTPException(status_code=400, detail="Invalid password")
        return v

#pydantic model for user password
class UserPassword(BaseModel):
    hashed_password: str

    @validator('hashed_password')
    def hashed_password_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" "):
            raise HTTPException(status_code=400, detail="Invalid password")
        return v

#pydantic model for user
class User(UserBase):
    uuid: str = Field(serialization_alias="id")
    conferences: list[Conference] = []
    is_active: bool
    class Config:
        orm_mode = True
