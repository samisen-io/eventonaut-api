from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime

class UserRoleBase(BaseModel):
    role_id: int
    user_id: int

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleUpdate(UserRoleBase):
    pass

class UserRoleInDBBase(UserRoleBase):
    id: int
    created_on: Optional[datetime] = None
    updated_on: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserRole(UserRoleInDBBase):
    pass

class UserRoleInDB(UserRoleInDBBase):
    pass