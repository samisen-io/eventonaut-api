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
    name = Column(String, index=True, unique=True)
    business_type = Column(String, index=True)
    description = Column(String, index=True)
    address = Column(String, index=True)
    logo_image_url = Column(String, index=True)
    website_url = Column(String, index=True)
    
    organization_user = relationship("Organization_User", back_populates="organization")

class Organization_User(Base):
    __tablename__ = "organization_user"

    id = Column(Integer, primary_key=True, index=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    uuid = Column(String, index=True, unique=True)
    organization_id = Column(Integer, ForeignKey("organization.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    organization = relationship("Organization", back_populates="organization_user")
    user = relationship("User", back_populates="organization_user")
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    email = Column(String, index=True, unique=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    hashed_password = Column(String)
    role = Column(String, index=True)
    timezone = Column(String, index=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    user_status_id = Column(Integer, ForeignKey("organizer_status.id"))
    profile_image_url = Column(String, index=True)
    is_archived = Column(Boolean, default=False)
    company = Column(String, index=True)
    business_type = Column(String, index=True)

    attendees = relationship("Attendee", back_populates="user")
    conferences = relationship("Conference", back_populates="owner")
    sessions = relationship("Session", back_populates="owner")
    settings = relationship("Settings", back_populates="owner")
    client = relationship("Client", back_populates="owner")
    venues = relationship("Venue", back_populates="owner")
    speakers = relationship("Speakers", back_populates="owner")
    sponsors = relationship("Sponsors", back_populates="owner")
    organizer_status = relationship("OrganizerStatus", back_populates="user")
    user_roles = relationship('User_Role', back_populates='user')
    organization_user = relationship("Organization_User", back_populates="user")
    
class Role(Base):
    __tablename__ = "role"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    name = Column(String, index=True)
    description = Column(String, index=True)
    
    user_roles = relationship('User_Role', back_populates='role')
    
class User_Role(Base):
    __tablename__ = "user_role"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    role_id = Column(Integer, ForeignKey("role.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship('User', back_populates='user_roles')
    role = relationship('Role', back_populates='user_roles')

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
    client_status_id = Column(Integer, ForeignKey("client_status.id"))
    is_archived = Column(Boolean, default=False)

    owner = relationship("User", back_populates="client")
    conferences = relationship("Conference", back_populates="client")
    client_status = relationship("ClientStatus", back_populates="client")
  
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
    conference_status_id = Column(Integer, ForeignKey("event_status.id"))
    is_archived = Column(Boolean, default=False)

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
    event_status = relationship("EventStatus", back_populates="conference")

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
    is_archived = Column(Boolean, default=False)

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
    session_status_id = Column(Integer, ForeignKey("session_status.id"))
    is_archived = Column(Boolean, default=False)

    conference = relationship("Conference", back_populates="sessions")
    owner = relationship("User", back_populates="sessions")
    agenda_session = relationship("AgendaSession", back_populates="session")
    sessions_speakers = relationship("SessionSpeakers", back_populates="session")
    session_status = relationship("Sessionstatus", back_populates="session")

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
    is_archived = Column(Boolean, default=False)

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
    is_archived = Column(Boolean, default=False)

    owner = relationship("User", back_populates="venues")
    conference = relationship("Conference", back_populates="venues")
    
class OrganizerStatus(Base):
    __tablename__ = "organizer_status"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    status = Column(String, index=True, unique=True)
    
    user = relationship("User", back_populates="organizer_status")

class ClientStatus(Base):
    __tablename__ = "client_status"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    status = Column(String, index=True, unique=True)
    
    client = relationship("Client", back_populates="client_status")
    
class EventStatus(Base):
    __tablename__ = "event_status"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    status = Column(String, index=True, unique=True)
    
    conference = relationship("Conference", back_populates="event_status")
    
class Sessionstatus(Base):
    __tablename__ = "session_status"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    status = Column(String, index=True, unique=True)
    
    session = relationship("Session", back_populates="session_status")
    
class AttendeeStatus(Base):
    __tablename__ = "attendee_status"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    status = Column(String, index=True, unique=True)