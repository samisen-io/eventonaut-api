from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
from .session_schemas import Session

#pydantic model for agenda create
class AgendaBase(BaseModel):
    name: str

    @validator('name')
    def name_must_contain_space(cls, v):
        if v is None or v.strip() == '' or v == 'string':
            raise HTTPException(status_code=400, detail="Invalid name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v

class AgendaCreate(AgendaBase):
    attendee_id: str
    conference_id: str
    sessions: list[str] = []

    @validator('sessions')
    def sessions_must_contain_at_least_one_session(cls, v):
        if v is None or len(v) == 0:
            raise HTTPException(status_code=400, detail="Invalid sessions")
        return v
    
    @validator('attendee_id')
    def attendee_id_must_contain_space(cls, v):
        if v is None or v.strip() == '' or v == 'string':
            raise HTTPException(status_code=400, detail="Invalid attendee id")
        return v
    
    @validator('conference_id')
    def conference_id_must_contain_space(cls, v):
        if v is None or v.strip() == '' or v == 'string':
            raise HTTPException(status_code=400, detail="Invalid conference id")
        return v

class AgendaUpdate(AgendaBase):
    attendee_id: str
    conference_id: str
    name: str | None = None
    sessions: list[str] | None = None

    @validator('attendee_id')
    def attendee_id_must_contain_space(cls, v):
        if v is None or v.strip() == '' or v == 'string':
            raise HTTPException(status_code=400, detail="Invalid attendee id")
        return v
    
    @validator('conference_id')
    def conference_id_must_contain_space(cls, v):
        if v is None or v.strip() == '' or v == 'string':
            raise HTTPException(status_code=400, detail="Invalid conference id")
        return v
    
    @validator('name')
    def name_must_contain_space(cls, v):
        if v.strip() == '' or v == 'string':
            raise HTTPException(status_code=400, detail="Invalid name")
        elif len(v) > 256:
            raise HTTPException(status_code=400, detail="Name too long")
        return v
    
    @validator('sessions')
    def sessions_must_contain_at_least_one_session(cls, v):
        if v == '':
            raise HTTPException(status_code=400, detail="Invalid sessions")
        for session_id in v:
            if session_id.strip() == '' or session_id == 'string':
                raise HTTPException(status_code=400, detail="Invalid session id")
        return v

#pydantic model for agenda
class Agenda(AgendaBase):
    uuid: str = Field(serialization_alias='id')
    sessions: list[Session] = []
    
    class Config:
        orm_mode = True