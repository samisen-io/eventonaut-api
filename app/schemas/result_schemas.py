from pydantic import BaseModel, validator, Field
from fastapi import HTTPException
from .conference_schemas import Conference

class User(BaseModel):
    pass

class Event(BaseModel):
    pass

class Session(BaseModel):
    pass

class Settings(BaseModel):
    pass

class Conference_Files(BaseModel):
    pass

class Attendee(BaseModel):
    pass

class Attendee_Conferences(BaseModel):
    pass

class Agenda(BaseModel):
    pass

class AgendaSession(BaseModel):
    pass

class LogoutToken(BaseModel):
    pass

class Client(BaseModel):
    pass

class Speakers(BaseModel):
    pass

class AITokens(BaseModel):
    pass