from pydantic import BaseModel, validator, Field
from fastapi import HTTPException

#pydantic model for attendeebase
class AttendeeBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    profile_image_url: str | None = None
    
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
    
    @validator('profile_image_url')
    def profile_image_url_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid profile image url")
        return v
    
#pydantic model for attendee create
class AttendeeCreate(AttendeeBase):
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

#pydantic model for attendee password
class AttendePassword(BaseModel):
    id: str
    hashed_password: str

    @validator('id')
    def id_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid id")
        return v
    
    @validator('hashed_password')
    def hashed_password_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string" or v.__contains__(" "):
            raise HTTPException(status_code=400, detail="Invalid password")
        elif len(v) < 8:
            raise HTTPException(status_code=400, detail="Password too short")
        elif len(v) > 16:
            raise HTTPException(status_code=400, detail="Password too long")
        return v

class AttendeeUpdate(BaseModel):
    id: str
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    profile_image_url: str | None = None

    @validator('id')
    def id_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid id")
        return v
    
    @validator('first_name')
    def first_name_is_not_empty(cls, v):
        if v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid first name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="First name too long")
        return v
    
    @validator('last_name')
    def last_name_is_not_empty(cls, v):
        if v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid last name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Last name too long")
        return v
    
    @validator('profile_image_url')
    def profile_image_url_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid profile image url")
        return v

#pydantic model for attendee
class Attendee(AttendeeBase):
    uuid: str = Field(serialization_alias="id")
    is_active: bool
    class Config:
        orm_mode = True