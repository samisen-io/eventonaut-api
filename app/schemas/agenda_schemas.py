from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
from .session_speaker_schema import SessionResponse

#pydantic model for agenda create
class AgendaBase(BaseModel):
    name: str

    @validator('name')
    def name_must_contain_space(cls, v):
        if v.strip() == '':
            raise ValueError("Name cannot be empty")
        elif len(v) > 256:
            raise ValueError("Name must be less than 256 characters")
        return v

class AgendaCreate(AgendaBase):
    conference_id: str
    sessions: list[str] = []

    @validator('sessions')
    def sessions_must_contain_at_least_one_session(cls, v):
        if len(v) == 0:
            raise ValueError("Sessions cannot be empty")
        for session_id in v:
            if session_id.strip() == '':
                raise ValueError("Invalid session id")
        return v
    
    @validator('conference_id')
    def conference_id_must_contain_space(cls, v):
        if v is None or v.strip() == '':
            raise ValueError("Invalid conference id")
        return v

class AgendaUpdate(AgendaBase):
    conference_id: str
    name: str | None = None
    sessions: list[str] = []

    @validator('conference_id')
    def conference_id_must_contain_space(cls, v):
        if v.strip() == '':
            raise ValueError("Invalid conference id")
        return v
    
    @validator('name')
    def name_must_contain_space(cls, v):
        if v is not None:
            if v.strip() == '':
                return None
            elif len(v) > 256:
                raise ValueError("Name must be less than 256 characters")
        return v
    
    @validator('sessions')
    def sessions_must_contain_at_least_one_session(cls, v):
        for session_id in v:
            if session_id.strip() == '':
                raise ValueError("Invalid session id")
        return v

#pydantic model for agenda
class Agenda(AgendaBase):
    uuid: str = Field(serialization_alias='id')
    sessions: list[SessionResponse] = []
    
    class Config:
        orm_mode = True