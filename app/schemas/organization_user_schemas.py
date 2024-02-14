from pydantic import BaseModel, Field


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