from pydantic import BaseModel, Field

# Base properties for Role for API request/response


class RoleBase(BaseModel):
    name: str
    description: str


# Properties to receive via API on creation


class RoleCreate(RoleBase):
    name: str


# Properties to receive via API on update


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