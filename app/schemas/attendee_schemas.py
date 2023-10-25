from pydantic import BaseModel
from .agenda_schemas import Agenda

#pydantic model for attendee create
class AttendeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    hased_password: str

#pydantic model for attendee
class Attendee(AttendeeCreate):
    id: int
    conference_id: int
    adenga: Agenda
    class Config:
        orm_mode = True