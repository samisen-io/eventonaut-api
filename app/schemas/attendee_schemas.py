from pydantic import BaseModel
from .agenda_schemas import Agenda

#pydantic model for attendeebase
class AttendeeBase(BaseModel):
    first_name: str
    last_name: str
    email: str

#pydantic model for attendee create
class AttendeeCreate(AttendeeBase):
    hased_password: str

#pydantic model for attendee password
class AttendePassword(BaseModel):
    id: int
    hased_password: str

class AttendeeUpdate(AttendeeBase):
    id: int

#pydantic model for attendee
class Attendee(AttendeeBase):
    id: int
    class Config:
        orm_mode = True