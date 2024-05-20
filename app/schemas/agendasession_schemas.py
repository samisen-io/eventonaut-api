from pydantic import BaseModel
from .session_schemas import Session
from typing import List

class AgendaSession(BaseModel):
    session: List[Session]

    class Config:
        orm_mode = True