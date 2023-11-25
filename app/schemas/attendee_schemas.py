from pydantic import BaseModel, validator, Field
from fastapi import HTTPException

#pydantic model for attendeebase
class AttendeeBase(BaseModel):
    id: int
    uuid: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None
    company: str | None = None
    bio: str | None = None
    share_my_profile: bool | None = None
    share_my_agenda: bool | None = None
    profile_image_url: str | None = None
    
    @validator('email')
    def email_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid email")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Email too long")
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
    
    @validator('title')
    def title_is_not_empty(cls, v):
        if v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid title")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Title too long")
        return v
    
    @validator('company')
    def company_is_not_empty(cls, v):
        if v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid company")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Company too long")
        return v
    
    @validator('bio')
    def bio_is_not_empty(cls, v):
        if v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid bio")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Bio too long")
        return v

    @validator('profile_image_url')
    def profile_image_url_is_not_empty(cls, v):
        if v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid profile image url")
        return v
    
#pydantic model for attendee create
class AttendeeCreate(BaseModel):
    email: str
    hashed_password: str

    @validator('email')
    def email_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid email")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Email too long")
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
    title: str | None = None
    company: str | None = None
    bio: str | None = None
    share_my_profile: bool | None = None
    share_my_agenda: bool | None = None
    profile_image_url: str | None = None

    @validator('id')
    def id_is_not_empty(cls, v):
        if v is None or v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid id")
        return v

    @validator('email')
    def email_is_not_empty(cls, v):
        if v.strip() == "" or v == "string":
            raise HTTPException(status_code=400, detail="Invalid email")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Email too long")
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
    
    @validator('title')
    def title_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                raise HTTPException(status_code=400, detail="Invalid title")
            elif len(v) > 256:
                raise HTTPException(status_code=400, detail="Title too long")
        return v
    
    @validator('company')
    def company_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                raise HTTPException(status_code=400, detail="Invalid company")
            elif len(v) > 256:
                raise HTTPException(status_code=400, detail="Company too long")
        return v
    
    @validator('bio')
    def bio_is_not_empty(cls, v):
        if v is not None:
            if v.strip() == "" or v == "string":
                raise HTTPException(status_code=400, detail="Invalid bio")
            elif len(v) > 256:
                raise HTTPException(status_code=400, detail="Bio too long")
        return v
    
    @validator('profile_image_url')
    def profile_image_url_is_not_empty(cls, v):
        if v is not None and (v.strip() == "" or v == "string"):
            raise HTTPException(status_code=400, detail="Invalid profile image url")
        return v

#pydantic model for attendee
class Attendee(AttendeeBase):
    is_active: bool
    class Config:
        orm_mode = True