from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, DateTime, DATE, TIME, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .database import Base

class Organization(Base):
    __tablename__ = "organization"

    id = Column(Integer, primary_key=True, index=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    uuid = Column(String, index=True, unique=True)
    name = Column(String, index=True)
    company = Column(String, index=True)
    business_type = Column(String, index=True)
    description = Column(String, index=True)
    address = Column(String, index=True)
    contact_email = Column(String, index=True)
    contact_phone = Column(String, index=True)
    logo_image_url = Column(String, index=True)
    website_url = Column(String, index=True)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    email = Column(String, index=True, unique=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    company = Column(String, index=True)
    business_type = Column(String, index=True)
    hashed_password = Column(String)
    role = Column(String, index=True)
    timezone = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    user_status_id = Column(Integer, ForeignKey("static_organizers.id"))
    isarchived = Column(Boolean, default=False)
    profile_image_url = Column(String, index=True)

    attendees = relationship("Attendee", back_populates="user")
    conferences = relationship("Conference", back_populates="owner")
    sessions = relationship("Session", back_populates="owner")
    settings = relationship("Settings", back_populates="owner")
    client = relationship("Client", back_populates="owner")
    venues = relationship("Venue", back_populates="owner")
    speakers = relationship("Speakers", back_populates="owner")
    sponsors = relationship("Sponsors", back_populates="owner")
    static_organizer = relationship("StaticOrganizer", back_populates="user")

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    contact_name = Column(String, index=True)
    contact_email = Column(String, index=True)
    contact_phone = Column(String, index=True)
    address = Column(String, index = True)
    profile_image_url = Column(String, index=True)
    client_status_id = Column(Integer, ForeignKey("static_clients.id"))
    isarchived = Column(Boolean, default=False)

    owner = relationship("User", back_populates="client")
    conferences = relationship("Conference", back_populates="client")
    static_client = relationship("StaticClient", back_populates="client")
  
#class to create conference table and add relationship to session table
class Conference(Base):
    __tablename__ = "conferences"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    client_id = Column(Integer, ForeignKey("clients.id"))
    name = Column(String, index=True)
    location = Column(String, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    start_date = Column(DATE, index=True)
    end_date = Column(DATE, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    conference_logo = Column(String, index=True)
    conference_banner_url = Column(String, index=True)
    assistant_id = Column(String, index=True)
    code = Column(String, index=True)
    timezone = Column(String, index=True)
    registration_link = Column(String, index=True)
    information_guide = Column(String, index=True)
    conference_status_id = Column(Integer, ForeignKey("static_events.id"))
    isarchived = Column(Boolean, default=False)

    client = relationship("Client", back_populates="conferences")
    owner = relationship("User", back_populates="conferences")
    sessions = relationship("Session", back_populates="conference")
    settings = relationship("Settings", back_populates="conference")
    agenda = relationship("Agenda", back_populates="conference")
    conference_files = relationship("Conference_Files", back_populates="conference")
    attendee_conference = relationship("Attendee_Conferences", back_populates="conference")
    aitokens = relationship("AITokens", back_populates="conference")
    promotions = relationship("Promotions", back_populates="conference")
    venues = relationship("Venue", back_populates="conference")
    sessions_speakers = relationship("SessionSpeakers", back_populates="conference")
    event_sponsors = relationship("EventSponsors", back_populates="conference")
    static_event = relationship("StaticEvent", back_populates="conference")

class Conference_Files(Base):
    __tablename__ = "conference_files"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    file_id = Column(String, index=True)

    conference = relationship("Conference", back_populates="conference_files")

class Speakers(Base):
    __tablename__ = "speakers"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    email = Column(String, index=True, unique=True)
    title = Column(String, index=True)
    bio = Column(String, index=True)
    profile_image_url = Column(String, index=True)
    isarchived = Column(Boolean, default=False)

    sessions_speakers = relationship("SessionSpeakers", back_populates="speaker")
    owner = relationship("User", back_populates="speakers")

class SessionSpeakers(Base):
    __tablename__ = "session_speakers"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    session_id = Column(Integer, ForeignKey("sessions.id"))
    speaker_id = Column(Integer, ForeignKey("speakers.id"))

    session = relationship("Session", back_populates="sessions_speakers")
    speaker = relationship("Speakers", back_populates="sessions_speakers")
    conference = relationship("Conference", back_populates="sessions_speakers")

# class to define session table
class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    name = Column(String, index=True)
    start_time = Column(TIME, index=True)
    end_time = Column(TIME, index=True)
    description = Column(String, index=True)
    date = Column(DATE, index=True) 
    location = Column(String, index=True)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    tags = Column(ARRAY(String), index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    session_image_url = Column(String, index=True)
    session_status_id = Column(Integer, ForeignKey("static_sessions.id"))
    isarchived = Column(Boolean, default=False)

    conference = relationship("Conference", back_populates="sessions")
    owner = relationship("User", back_populates="sessions")
    agenda_session = relationship("AgendaSession", back_populates="session")
    sessions_speakers = relationship("SessionSpeakers", back_populates="session")
    static_session = relationship("StaticSession", back_populates="session")

#class to define settings table with id, conference id as foreign key, created on and updated on as datetime and body as a string
class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    body = Column(JSONB, index=True)

    conference = relationship("Conference", back_populates="settings")
    owner = relationship("User", back_populates="settings")

# class to define attendee table with id, conference id as foreign key, created on and updated on as datetime and body as a string
class Attendee(Base):
    __tablename__ = "attendees"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, index=True)
    bio = Column(String, index=True)
    share_my_profile = Column(Boolean, default=False)
    share_my_agenda = Column(Boolean, default=False)
    thread_id = Column(String, index=True)

    user = relationship("User", back_populates="attendees")
    agenda = relationship("Agenda", back_populates="attendees")
    agenda_session = relationship("AgendaSession", back_populates="attendees")
    attendee_conference = relationship("Attendee_Conferences", back_populates="attendee")
    aitokens = relationship("AITokens", back_populates="attendee")

class Attendee_Conferences(Base):
    __tablename__ = "attendee_conferences"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    attendee_id = Column(Integer, ForeignKey("attendees.id"))
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    is_registered = Column(Boolean, default=False)

    attendee = relationship("Attendee", back_populates="attendee_conference")
    conference = relationship("Conference", back_populates="attendee_conference")

# class to define agenda table with id, conference id as foreign key, created on and updated on as datetime and body as a string
class Agenda(Base):
    __tablename__ = "agenda"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    name = Column(String, index=True)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    attendee_id = Column(Integer, ForeignKey("attendees.id"))

    conference = relationship("Conference", back_populates="agenda")
    attendees = relationship("Attendee", back_populates="agenda")
    agenda_session = relationship("AgendaSession", back_populates="agenda")

# class to define aganda session table with id, conference id as foreign key, created on and updated on as datetime and body as a string
class AgendaSession(Base):
    __tablename__ = "agenda_session"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    agenda_id = Column(Integer, ForeignKey("agenda.id"))
    session_id = Column(Integer, ForeignKey("sessions.id"))
    attendee_id = Column(Integer, ForeignKey("attendees.id"))
    date = Column(DATE, index=True)
    start_time = Column(TIME, index=True)
    end_time = Column(TIME, index=True)

    agenda = relationship("Agenda", back_populates="agenda_session")
    session = relationship("Session", back_populates="agenda_session")
    attendees = relationship("Attendee", back_populates="agenda_session")

class AITokens(Base):
    __tablename__ = "aitokens"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    attendee_id = Column(Integer, ForeignKey("attendees.id"))
    successful_requests = Column(Integer, default=0)
    total_cost = Column(Float, default=0)
    total_tokens = Column(Integer, default=0)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    processing_time = Column(TIME, index=True, default="00:00:00")

    conference = relationship("Conference", back_populates="aitokens")
    attendee = relationship("Attendee", back_populates="aitokens")

class LogoutToken(Base):
    __tablename__ = "logout_tokens"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    token_jti = Column(String, index=True, unique=True)
    is_invalidated = Column(Boolean, default=False)
    expires_on = Column(DateTime)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)

class Promotions(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    todate = Column(DATE)
    fromdate = Column(DATE)
    image_url = Column(String, index=True)
    promotion_name = Column(String, index=True)
    rank = Column(Integer, default=0)

    conference = relationship("Conference", back_populates="promotions")

class Sponsors(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    description = Column(String, index=True)
    email = Column(String, index=True)
    contact_name = Column(String, index=True)
    contact_phone = Column(String, index=True)
    logo_image_url = Column(String, index=True)
    sponsorship_level = Column(String, index=True)
    isarchived = Column(Boolean, default=False)

    owner = relationship("User", back_populates="sponsors")
    event_sponsors = relationship("EventSponsors", back_populates="sponsors")

class EventSponsors(Base):
    __tablename__ = "event_sponsors"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"))

    conference = relationship("Conference", back_populates="event_sponsors")
    sponsors = relationship("Sponsors", back_populates="event_sponsors")

class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    location = Column(String, index=True)
    address = Column(String, index=True)
    geo_location = Column(String, index=True)
    isarchived = Column(Boolean, default=False)

    owner = relationship("User", back_populates="venues")
    conference = relationship("Conference", back_populates="venues")
    
class StaticOrganizer(Base):
    __tablename__ = "static_organizers"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    status = Column(String, index=True, unique=True)
    
    user = relationship("User", back_populates="static_organizer")

class StaticClient(Base):
    __tablename__ = "static_clients"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    status = Column(String, index=True, unique=True)
    
    client = relationship("Client", back_populates="static_client")
    
class StaticEvent(Base):
    __tablename__ = "static_events"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    status = Column(String, index=True, unique=True)
    
    conference = relationship("Conference", back_populates="static_event")
    
class StaticSession(Base):
    __tablename__ = "static_sessions"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    status = Column(String, index=True, unique=True)
    
    session = relationship("Session", back_populates="static_session")
    
class StaticAttendee(Base):
    __tablename__ = "static_attendees"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    status = Column(String, index=True, unique=True)