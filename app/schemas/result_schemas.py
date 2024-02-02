from pydantic import BaseModel, Field
from datetime import date, time
from typing import List, Optional

class User(BaseModel):
    uuid: str = Field(serialization_alias="id")
    email: str
    first_name: str
    last_name: str
    company: str
    business_type: str
    timezone: str
    is_active: bool
    rank: int

class Event(BaseModel):
    uuid: str = Field(serialization_alias="id")
    name: str
    location: str
    start_date: date
    end_date: date
    description: str
    conference_logo: str | None = None
    timezone: str | None = None
    registration_link: str | None = None
    information_guide: str
    rank: int

class Speakers(BaseModel):
    uuid: str = Field(serialization_alias="id")
    name: str
    title: str
    bio: str
    profile_image_url: str | None = None
    rank: int

class Session(BaseModel):
    uuid: str = Field(serialization_alias="id")
    name: str
    start_time: time
    end_time: time
    description: str
    date: date
    location: str
    speakers: list[str] | None = None
    tags: list[str]
    rank: int

class Settings(BaseModel):
    uuid: str = Field(serialization_alias="id")
    body: dict
    rank: int

class Conference_Files(BaseModel):
    pass

class Attendee(BaseModel):
    uuid: str = Field(serialization_alias="id")
    email: str
    first_name: str
    last_name: str
    title: str
    company: str
    bio: str
    share_my_profile: bool
    share_my_agenda: bool
    profile_image_url: str
    is_active: bool
    rank: int

class Attendee_Conferences(BaseModel):
    pass

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