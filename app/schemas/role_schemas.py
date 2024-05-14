from pydantic import BaseModel, Field

class RoleBase(BaseModel):
    name: str
    description: str

class RoleCreate(RoleBase):
    name: str

class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    
class RoleResponse(RoleBase):
    class Config:
        orm_mode = True

class Role(RoleBase):
    uuid: str = Field(serialization_alias="id")
    
    class Config:
        orm_mode = True