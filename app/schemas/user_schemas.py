from typing import List
from pydantic import BaseModel, Field, field_validator, ValidationInfo
import logging
from ..static_enums import organizer
from ..static_enums.role import RoleEnum
from ..url_validator import check_url

class UserBase(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None
    status: str | None = None
    company: str | None = None
    timezone: str | None = None
    profile_image_url: str | None = None
    list_of_roles: List[str] | None = None

    @field_validator('email')
    @classmethod
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} should be less than 256 characters")
            raise ValueError(f"{info.field_name} should be less than 256 characters")
        return v
    
    @field_validator("status")
    @classmethod
    def check_status(cls, v):
        v = v.upper()
        if v not in list(organizer.OrganizerEnum.__members__):
            logging.exception("Invalid status")
            raise ValueError("Invalid status")
        return v
    
    @field_validator('timezone')
    @classmethod
    def optional_field_validation(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            max_len = 50 if info.field_name == "timezone" else 256
            if len(v) > max_len:
                logging.exception(f"{info.field_name} should be less than {max_len} characters")
                raise ValueError(f"{info.field_name} should be less than {max_len} characters")
        return v
    
    @field_validator('profile_image_url')
    @classmethod
    def validate_url(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            if v is not None:
                try:
                    if not check_url(v):
                        raise ValueError(f"Broken {info.field_name} link or invalid url")
                except Exception as e:
                    raise ValueError(f"Broken {info.field_name} link or invalid url - {str(e)}")
        return v
    
    @field_validator('list_of_roles')
    @classmethod
    def check_role(cls, v):
        if v is not None:
            for role in v:
                if role not in list(RoleEnum.__members__):
                    raise ValueError("Invalid role")
        return v
    
class UserCreate(UserBase):
    hashed_password: str

    @field_validator('hashed_password')
    @classmethod
    def hashed_password_is_not_empty(cls, v):
        if v.strip() == "" or v.__contains__(" "):
            logging.exception("Invalid password")
            raise ValueError("Invalid password")
        if not 8 <= len(v) <= 16:
            logging.exception("Password should be between 8 and 16 characters")
            raise ValueError("Password should be between 8 and 16 characters")
        return v
    
class UserBaseUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    status: str | None = None
    timezone: str |None = None
    profile_image_url: str |None = None
    list_of_roles: List[str] | None = None

    @field_validator('first_name','last_name','timezone','profile_image_url')
    @classmethod
    def user_is_not_empty(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            max_len = 50 if info.field_name == "timezone" else 256
            if len(v) > max_len:
                logging.exception(f"{info.field_name} should be less than {max_len} characters")
                raise ValueError(f"{info.field_name} should be less than {max_len} characters")
        return v
    
    @field_validator("status")
    @classmethod
    def check_status(cls, v):
        if v is not None:
            if v.strip() == "":
                return None
            v = v.upper()
            if v not in list(organizer.OrganizerEnum.__members__):
                raise ValueError("Invalid status")
        return v
    
    @field_validator('profile_image_url')
    @classmethod
    def validate_url(cls, v, info: ValidationInfo):
        if v is not None:
            if v.strip() == "":
                return None
            if v is not None:
                try:
                    if not check_url(v):
                        raise ValueError(f"Broken {info.field_name} link or invalid url")
                except Exception as e:
                    raise ValueError(f"Broken {info.field_name} link or invalid url - {str(e)}")
        return v


class UserPasswordUpdate(BaseModel):
    old_password: str
    new_password: str

    @field_validator('old_password','new_password')
    @classmethod
    def password_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "" or v.__contains__(" "):
            logging.exception(f"Invalid {info.field_name}")
            raise ValueError(f"Invalid {info.field_name}")
        if not 8 <= len(v) <= 16:
            logging.exception(f"{info.field_name} should be between 8 and 16 characters")
            raise ValueError(f"{info.field_name} should be between 8 and 16 characters")
        return v

class User(BaseModel):
    uuid: str = Field(serialization_alias="id")
    email: str
    first_name: str | None = None
    last_name: str | None = None
    status: str | None = None
    company: str | None = None
    timezone: str | None = None
    profile_image_url: str | None = None
    list_of_roles: List[str] | None = None
    is_active: bool
    
    class Config:
        orm_mode = True
 
class Role(BaseModel):
    id: int
    description: str
    uuid: str
    name: str
 
class UserRoles(BaseModel):
    uuid: str
    role_id: int 
    role: Role
       
class OrgResp(BaseModel):
    id: int
    uuid: str
    organization_id: int
    user_id: int   
    
class UserAuthentication(User):
    id: int
    role: str
    user_roles: List[UserRoles]
    organization_user: list[OrgResp]

class UserAuthorization(BaseModel):
    id: int
    uuid: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    hashed_password: str
    is_active: bool
    is_verified: bool
    is_archived: bool
    user_status_id: int | None = None
    role: List[str] | None = None
    
class OtpVerification(BaseModel):
    email: str
    otp: str
    
    @field_validator('email')
    def field_is_not_empty(cls, v, info: ValidationInfo):
        if v.strip() == "":
            logging.exception(f"{info.field_name} cannot be empty")
            raise ValueError(f"{info.field_name} cannot be empty")
        elif len(v) > 256:
            logging.exception(f"{info.field_name} should be less than 256 characters")
            raise ValueError(f"{info.field_name} should be less than 256 characters")
        return v