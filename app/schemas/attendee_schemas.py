from pydantic import BaseModel, validator, Field, field_validator, ValidationInfo
from fastapi import HTTPException, status
from ..static_enums import attendee

#pydantic model for attendeebase
class AttendeeBase(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None
    company: str | None = None
    bio: str | None = None
    share_my_profile: bool | None = None
    share_my_agenda: bool | None = None
    profile_image_url: str | None = None
    status: str | None = None
    
    @validator('email')
    def email_is_not_empty(cls, v):
        if v.strip() == "":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Email too long")
        return v

    @field_validator('first_name','last_name','title','company','bio','profile_image_url')
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} must be less than 256 characters")
        return v
    
    @field_validator("status")
    def check_status(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            v = v.upper()
            if v not in list(attendee.AttendeeEnum.__members__):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
        return v
    
#pydantic model for attendee create
class AttendeeCreate(BaseModel):
    email: str
    hashed_password: str

    @validator('email')
    def email_is_not_empty(cls, v):
        if v.strip() == "":
            raise HTTPException(status_code=400, detail="Invalid email")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Email too long")
        return v

    @validator('hashed_password')
    def hashed_password_is_not_empty(cls, v):
        if v.strip() == "" or v.__contains__(" "):
            raise HTTPException(status_code=400, detail="Invalid password")
        elif len(v) < 8:
            raise HTTPException(status_code=400, detail="Password too short")
        elif len(v) > 16:
            raise HTTPException(status_code=400, detail="Password too long")
        return v

#pydantic model for attendee password
class AttendePassword(BaseModel):
    old_password: str
    new_password: str
    
    @validator('old_password')
    def old_password_is_not_empty(cls, v):
        if v.strip() == "" or v.__contains__(" "):
            raise HTTPException(status_code=400, detail="Invalid password")
        elif len(v) < 8:
            raise HTTPException(status_code=400, detail="Old password too short")
        elif len(v) > 16:
            raise HTTPException(status_code=400, detail="Old password too long")
        return v
    
    @validator('new_password')
    def new_password_is_not_empty(cls, v):
        if v.strip() == "" or v.__contains__(" "):
            raise HTTPException(status_code=400, detail="Invalid password")
        elif len(v) < 8:
            raise HTTPException(status_code=400, detail="New password too short")
        elif len(v) > 16:
            raise HTTPException(status_code=400, detail="New password too long")
        return v

class AttendeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None
    company: str | None = None
    bio: str | None = None
    share_my_profile: bool | None = None
    share_my_agenda: bool | None = None
    profile_image_url: str | None = None
    status: str | None = None

    @field_validator('first_name','last_name','title','company','bio','profile_image_url')
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{info.field_name} must be less than 256 characters")
        return v
    
    @field_validator("status")
    def check_status(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            v = v.upper()
            if v not in list(attendee.AttendeeEnum.__members__):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
        return v
    

#pydantic model for attendee
class Attendee(AttendeeBase):
    uuid: str = Field(serialization_alias="id")
    is_active: bool
    
    class Config:
        orm_mode = True