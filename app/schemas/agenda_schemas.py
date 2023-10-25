from pydantic import BaseModel
from .agendasession_schemas import AgendaSession

#pydantic model for agenda create
class AgendaCreate(BaseModel):
    name: str

#pydantic model for agenda
class Agenda(AgendaCreate):
    id: int
    conference_id: int
    attendee_id: int
    sessions: list[AgendaSession] = []
    class Config:
        orm_mode = True