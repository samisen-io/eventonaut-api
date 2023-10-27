from pydantic import BaseModel
from datetime import date
from .settings_schemas import Settings
from .session_schemas import Session

#pydantic model for conference create
class ConferenceCreate(BaseModel):
    name: str
    location: str
    start_date: date
    end_date: date
    description: str | None = None

class ConferenceUpdate(ConferenceCreate):
    id: int

#pydantic model for conference
class Conference(ConferenceCreate):
    id: int
    owner_id: int
    sessions: list[Session] = []
    settings: list[Settings] = []
    class Config:
        orm_mode = True