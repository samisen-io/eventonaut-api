from pydantic import BaseModel

#pydantic model for session create
class SessionCreate(BaseModel):
    name: str
    start_time: str
    end_time: str
    description: str | None = None

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

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    conferences: list[Conference] = []
    class Config:
        orm_mode = True
