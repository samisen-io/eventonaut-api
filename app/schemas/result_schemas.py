from pydantic import BaseModel, Field
from datetime import date, time
from typing import List, Optional
from ..schemas import venue_schemas, conference_schemas, speaker_schemas, session_schemas, attendee_schemas

class Event(conference_schemas.ConferenceBase):
    uuid: str = Field(serialization_alias="id")
    venue_details: venue_schemas.VenueResponse
    rank: int

class Speakers(speaker_schemas.SpeakerBase):
    uuid: str = Field(serialization_alias="id")
    rank: int

class Session(session_schemas.SessionBase):
    uuid: str = Field(serialization_alias="id")
    speakers: list[str] | None = None
    rank: int

class Attendee(attendee_schemas.AttendeeBase):
    uuid: str = Field(serialization_alias="id")
    is_active: bool
    rank: int

class Agenda(BaseModel):
    uuid: str = Field(serialization_alias="id")
    name: str
    rank: int

class AgendaSession(BaseModel):
    session: List[Session]
    rank: int

class LogoutToken(BaseModel):
    pass

class Client(BaseModel):
    uuid: str = Field(serialization_alias="id")
    name: str
    contact_name: str
    contact_email: str
    contact_phone: str
    profile_image_url: str
    rank: int

class AITokens(BaseModel):
    uuid: str = Field(serialization_alias="id")
    conference_id: str
    attendee_id: str
    successful_requests: int
    total_cost: float
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int
    processing_time: float
    rank: int