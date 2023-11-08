from pydantic import BaseModel
from .session_schemas import Session
from typing import List

#pydantic model for agenda_session
class AgendaSession(BaseModel):
    session: List[Session]

    class Config:
        orm_mode = True