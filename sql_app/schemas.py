from pydantic import BaseModel

class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    class Config:
        orm_mode = True

#pydantic model for conference
class Conference(BaseModel):
    id: int
    name: str
    location: str
    start_date: str
    end_date: str
    description: str | None = None
    owner_id: int

#pydantic model for conference create
class ConferenceCreate(Conference):
    pass