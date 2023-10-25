from pydantic import BaseModel
from datetime import date, time

# #pydantic model for agenda_session create
# class AgendaSessionCreate(BaseModel):

#pydantic model for agenda_session
class AgendaSession(BaseModel):
    id: int
    date: date
    start_time: time
    end_time: time
    attendee_id: int
    session_id: int
    conference_id: int
    class Config:
        orm_mode = True