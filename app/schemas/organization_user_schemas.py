from typing import List
from pydantic import BaseModel, Field
from .user_schemas import User

class DeleteResponse(BaseModel):
    message: str
    
class Organization_UserBase(BaseModel):
    organization_id: str
    user_id: str

class Organization_UserUpdate(BaseModel):
    organization_id: str
    user_id: str
    id: str

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