from pydantic import BaseModel, Field

# Base properties for Role for API request/response


class RoleBase(BaseModel):
    name: str | None = None
    description: str | None = None


# Properties to receive via API on creation


class RoleCreate(RoleBase):
    name: str


# Properties to receive via API on update


class RoleUpdate(RoleBase):
    id: str
    name: str
    description: str


# Properties to return via API


class Role(RoleBase):
    uuid: str = Field(serialization_alias="id")
    name: str

    class Config:
        orm_mode = True