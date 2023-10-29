from pydantic import BaseModel
from .conference_schemas import Conference

#pydantic model user base
class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    account_type: str
    bussiness_type: str

#pydantic model for user create
class UserCreate(UserBase):
    hashed_password: str

#pydantic model for user password
class UserPassword(BaseModel):
    hashed_password: str

#pydantic model for user
class User(UserBase):
    id: int
    is_active: bool
    class Config:
        orm_mode = True
