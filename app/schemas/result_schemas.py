from pydantic import BaseModel, Field
from datetime import date, time
from typing import List, Optional
from ..schemas import venue_schemas, conference_schemas, speaker_schemas, session_schemas, attendee_schemas, client_schemas

class Conference(conference_schemas.ConferenceBase):
    uuid: str = Field(serialization_alias="id")
    venue: venue_schemas.VenueResponse = Field(default=None)
    location: str
    rank: int

class Speakers(speaker_schemas.SpeakerBase):
    uuid: str = Field(serialization_alias="id")
    rank: int

class Session(session_schemas.SessionBase):
    uuid: str = Field(serialization_alias="id")
    #speakers: list[str] | None = None
    speakers: list[speaker_schemas.Speaker]
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
    
def convert_to_dict(obj):
    if hasattr(obj, "__dict__"):
        data = obj.__dict__.copy()
        data.pop('_sa_instance_state', None)
        return data
    else:
        raise TypeError("Object must be an instance of a SQLAlchemy Model")