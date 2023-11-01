from pydantic import BaseModel
from datetime import date, time

#pydantic model for session create
class SessionCreate(BaseModel):
    name: str
    start_time: time
    end_time: time
    description: str 
    date: date
    location: str 
    conference_id:int

#pydantic model for session
class Session(SessionCreate):
    id: int
    owner_id: int
    class Config:
        orm_mode = True

#pydantic model for session update
class SessionUpdate(SessionCreate):
    id: int
    class Config:
        orm_mode = True