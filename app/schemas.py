from pydantic import BaseModel
from datetime import datetime

#pydantic model for session create
class SessionCreate(BaseModel):
    name: str
    start_time: str
    end_time: str
    description: str | None = None
    date: str | None = None
    location: str | None = None

#pydantic model for session
class Session(SessionCreate):
    id: int
    conference_id: int
    class Config:
        orm_mode = True

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
    sessions: list[Session] = []
    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    account_type: str
    bussiness_type: str

#pydantic model for user create
class UserCreate(UserBase):
    hashed_password: str

class User(UserBase):
    id: int
    is_active: bool
    conferences: list[Conference] = []
    class Config:
        orm_mode = True

#pydantic model for settings
class Settings(BaseModel):
    id: int
    body: dict
    conference_id: int
    created_on: datetime
    updated_on: datetime
    class Config:
        orm_mode = True