from pydantic import BaseModel

#pydantic model for conference create
class ConferenceCreate(BaseModel):
    name: str
    location: str
    start_date: str
    end_date: str
    description: str | None = None

#pydantic model for conference
class Conference(ConferenceCreate):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    conferences: list[Conference] = []
    class Config:
        orm_mode = True
