from pydantic import BaseModel
from datetime import date, time

#pydantic model for settings
class SettingsCreate(BaseModel):
    body: dict

#pydantic model for settings
class Settings(SettingsCreate):
    id: int
    conference_id: int
    owner_id: int
    class Config:
        orm_mode = True

#pydantic model for session create
class SessionCreate(BaseModel):
    name: str
    start_time: time
    end_time: time
    description: str 
    date: date
    location: str 

#pydantic model for session
class Session(SessionCreate):
    id: int
    owner_id: int
    conference_id: int
    class Config:
        orm_mode = True

#pydantic model for conference create
class ConferenceCreate(BaseModel):
    name: str
    location: str
    start_date: date
    end_date: date
    description: str | None = None

#pydantic model for conference
class Conference(ConferenceCreate):
    id: int
    owner_id: int
    sessions: list[Session] = []
    settings: list[Settings] = []
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

#pydantic model for user password
class UserPassword(BaseModel):
    hashed_password: str

class User(UserBase):
    id: int
    is_active: bool
    conferences: list[Conference] = []
    class Config:
        orm_mode = True
