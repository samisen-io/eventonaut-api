from typing import List
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from .user_schemas import User
from ..static_enums import organizer

class Organization_UserBase(BaseModel):
    organization_id: str
    user_id: str

class Organization_UserUpdate(BaseModel):
    id: str
    first_name: str | None = None
    last_name: str | None = None
    status: str | None = None
    timezone: str |None = None
    profile_image_url: str |None = None
    
    @field_validator("id")
    @classmethod
    def check_id(cls, v):
        if v is not None:
            if v.strip() == "":
                raise ValueError("Invalid id")
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

class Organization_UserUpdateResponse(BaseModel):
    id: str
    uuid: str = Field(serialization_alias="user_id")
    first_name: str | None = None
    last_name: str | None = None
    status: str | None = None
    timezone: str |None = None
    profile_image_url: str |None = None
    list_of_roles: List[str] | None = None

class Organization_UserCreate(Organization_UserBase):
    pass

class Organization_User(Organization_UserBase):
    uuid: str = Field(serialization_alias="id")
    
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    uuid: str = Field(serialization_alias="id")
    email: str

class OrganizationBase(BaseModel):
    uuid: str = Field(serialization_alias="id")
    name: str

class OrganizationUserBase(BaseModel):
    uuid: str = Field(serialization_alias="id")
    user: User

class OrganizationUsersResponse(BaseModel):
    organization_uuid: str = Field(serialization_alias="organization_id")
    organization_name: str
    users: List[OrganizationUserBase]

class UserOrganizationsResponse(BaseModel):
    user_id: str
    organizations: List[OrganizationBase]