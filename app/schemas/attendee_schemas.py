from pydantic import BaseModel, validator, Field, field_validator, ValidationInfo
from ..static_enums import attendee
from ..url_validator import check_url

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
            raise ValueError("Email cannot be empty")
        elif len(v) > 256:
            raise ValueError("Email must be less than 256 characters")
        return v

    @field_validator('first_name','last_name','title','company','bio','profile_image_url')
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            elif len(v) > 256:
                raise ValueError(f"{info.field_name} must be less than 256 characters")
        return v
    
    @field_validator("status")
    def check_status(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            v = v.upper()
            if v not in list(attendee.AttendeeEnum.__members__):
                raise ValueError("Invalid status")
        return v
    
    @field_validator('profile_image_url')
    def validate_profile_image_url(cls, v, info: ValidationInfo):
        if v is not None:
            if not check_url(v):
                raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v
    
#pydantic model for attendee create
class AttendeeCreate(BaseModel):
    email: str
    hashed_password: str

    @validator('email')
    def email_is_not_empty(cls, v):
        if v.strip() == "":
            raise ValueError("Email cannot be empty")
        elif len(v) > 256:
            raise ValueError("Email must be less than 256 characters")
        return v

    @validator('hashed_password')
    def hashed_password_is_not_empty(cls, v):
        if v.strip() == "" or v.__contains__(" "):
            raise ValueError("Password cannot be empty")
        elif len(v) < 8:
            raise ValueError("Password too short")
        elif len(v) > 16:
            raise ValueError("Password too long")
        return v

#pydantic model for attendee password
class AttendePassword(BaseModel):
    old_password: str
    new_password: str
    
    @validator('old_password')
    def old_password_is_not_empty(cls, v):
        if v.strip() == "" or v.__contains__(" "):
            raise ValueError("Old password cannot be empty")
        elif len(v) < 8:
            raise ValueError("Old password too short")
        elif len(v) > 16:
            raise ValueError("Old password too long")
        return v
    
    @validator('new_password')
    def new_password_is_not_empty(cls, v):
        if v.strip() == "" or v.__contains__(" "):
            raise ValueError("New password cannot be empty")
        elif len(v) < 8:
            raise ValueError("New password too short")
        elif len(v) > 16:
            raise ValueError("New password too long")
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
                raise ValueError(f"{info.field_name} must be less than 256 characters")
        return v
    
    @field_validator("status")
    def check_status(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            v = v.upper()
            if v not in list(attendee.AttendeeEnum.__members__):
                raise ValueError("Invalid status")
        return v

    @field_validator('profile_image_url')
    def validate_profile_image_url(cls, v, info: ValidationInfo):
        if v is not None:
            if not check_url(v):
                raise ValueError(f"Broken {info.field_name} link or invalid url")
        return v

#pydantic model for attendee
class Attendee(AttendeeBase):
    uuid: str = Field(serialization_alias="id")
    is_active: bool
    
    class Config:
        orm_mode = True