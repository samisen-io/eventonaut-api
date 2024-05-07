from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, DateTime, DATE, TIME, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, backref
from sqlalchemy import UniqueConstraint
from .database import Base

class Organization(Base):
    __tablename__ = "organization"

    id = Column(Integer, primary_key=True, index=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    uuid = Column(String, index=True, unique=True)
    name = Column(String, index=True)
    business_type = Column(String, index=True)
    description = Column(String, index=True)
    address = Column(String, index=True)
    logo_image_url = Column(String, index=True)
    website_url = Column(String, index=True)
    external_id = Column(String, index=True)
    is_archived = Column(Boolean, default=False)
    
    organization_settings = relationship("OrganizationSettings", back_populates="organization")
    organization_user = relationship("Organization_User", back_populates="organization")
    clients = relationship("Client", back_populates="organization")
    conferences = relationship("Conference", back_populates="organization")
    backdrop_gallery = relationship("BackdropGallery", back_populates="organization")
    speakers = relationship("Speakers", back_populates="organization")
    sessions = relationship("Session", back_populates="organization")
    promotions = relationship("Promotions", back_populates="organization")
    sponsors = relationship("Sponsors", back_populates="organization")
    venues = relationship("Venue", back_populates="organization")
    event_documents = relationship("EventDocuments", back_populates="organization")
    session_documents = relationship("SessionDocuments", back_populates="organization")
    exhibitors = relationship("Exhibitor", back_populates="organization")
    exhibitor_documents = relationship("ExhibitorDocuments", back_populates="organization")

class Organization_User(Base):
    __tablename__ = "organization_user"

    id = Column(Integer, primary_key=True, index=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    uuid = Column(String, index=True, unique=True)
    organization_id = Column(Integer, ForeignKey("organization.id"))
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

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
    # conferences = relationship("Conference", back_populates="owner")
    #sessions = relationship("Session", back_populates="owner")
    #settings = relationship("Settings", back_populates="owner")
    # client = relationship("Client", back_populates="owner")
    # speakers = relationship("Speakers", back_populates="owner")
    # sponsors = relationship("Sponsors", back_populates="owner")
    organizer_status = relationship("OrganizerStatus", back_populates="user")
    user_roles = relationship('User_Role', back_populates='user')
    organization_user = relationship("Organization_User", back_populates="user")
    # backdrop_gallery = relationship("BackdropGallery", back_populates="User")
    
    @property
    def status(self):
        return self.organizer_status.status.upper()
    
    @property
    def organization_id(self):
        return self.organization_user.organization_id
    
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

    __table_args__ = (UniqueConstraint('user_id', 'role_id', name='_user_role_uc'),)
    
class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    # owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    contact_name = Column(String, index=True)
    contact_email = Column(String, index=True)
    contact_phone = Column(String, index=True)
    address = Column(String, index = True)
    profile_image_url = Column(String, index=True)
    client_status_id = Column(Integer, ForeignKey("client_status.id"))
    is_archived = Column(Boolean, default=False)
    organization_id = Column(Integer, ForeignKey("organization.id"))

    # owner = relationship("User", back_populates="client")
    conferences = relationship("Conference", back_populates="client")
    client_status = relationship("ClientStatus", back_populates="client")
    organization = relationship("Organization", back_populates="clients")
    
    @property
    def status(self):
        return self.client_status.status.upper()
  
#class to create conference table and add relationship to session table
class Conference(Base):
    __tablename__ = "conferences"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    client_id = Column(Integer, ForeignKey("clients.id"))
    name = Column(String, index=True)
    venue_id = Column(Integer, ForeignKey("venues.id"))
    start_date = Column(DATE, index=True)
    end_date = Column(DATE, index=True)
    description = Column(String, index=True)
    # owner_id = Column(Integer, ForeignKey("users.id"))
    conference_logo = Column(String, index=True)
    conference_banner_url = Column(String, index=True)
    assistant_id = Column(String, index=True)
    code = Column(String, index=True)
    timezone = Column(String, index=True)
    registration_link = Column(String, index=True)
    information_guide = Column(String, index=True)
    conference_status_id = Column(Integer, ForeignKey("event_status.id"))
    is_archived = Column(Boolean, default=False)
    external_id = Column(String, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"))
    event_type = Column(String, index=True)

    client = relationship("Client", back_populates="conferences")
    # owner = relationship("User", back_populates="conferences")
    sessions = relationship("Session", back_populates="conference")
    settings = relationship("Settings", back_populates="conference")
    agenda = relationship("Agenda", back_populates="conference")
    conference_files = relationship("Conference_Files", back_populates="conference")
    attendee_conference = relationship("Attendee_Conferences", back_populates="conference")
    aitokens = relationship("AITokens", back_populates="conference")
    promotions = relationship("Promotions", back_populates="conference")
    venue = relationship("Venue", back_populates="conference")
    sponsors = relationship("Sponsors", secondary="event_sponsors", back_populates="conference", overlaps="event_sponsors")
    event_status = relationship("EventStatus", back_populates="conference")
    backdrop_gallery = relationship("BackdropGallery", back_populates="conference")
    event_documents = relationship("EventDocuments", back_populates="conference")
    organization = relationship("Organization", back_populates="conferences")
    exhibitors = relationship("Exhibitor", secondary="event_exhibitor", backref=backref("conferences", lazy='dynamic'))
    attendee_exhibitors = relationship("AttendeeExhibitors", back_populates="conference")
    
    @property
    def status(self):
        return self.event_status.status.upper()
    
    @property
    def location(self):
        return self.venue.location
    
class BackdropGallery(Base):
    __tablename__ = "backdrop_gallery"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    name = Column(String, index=True)
    size = Column(Float, index=True)
    # owner_id = Column(Integer, ForeignKey("users.id"))
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    backdrop_url = Column(String, index=True)
    is_archived = Column(Boolean, default=False)
    organization_id = Column(Integer, ForeignKey("organization.id"))
    
    conference = relationship("Conference", back_populates="backdrop_gallery")
    # User = relationship("User", back_populates="backdrop_gallery")
    organization = relationship("Organization", back_populates="backdrop_gallery")
    
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
    # owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    email = Column(String, index=True, unique=True)
    title = Column(String, index=True)
    bio = Column(String, index=True)
    profile_image_url = Column(String, index=True)
    is_archived = Column(Boolean, default=False)
    organization_id = Column(Integer, ForeignKey("organization.id"))

    sessions = relationship("Session", secondary="session_speakers", back_populates="speakers")
    # owner = relationship("User", back_populates="speakers")
    organization = relationship("Organization", back_populates="speakers")

class SessionSpeakers(Base):
    __tablename__ = "session_speakers"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    session_id = Column(Integer, ForeignKey("sessions.id"))
    speaker_id = Column(Integer, ForeignKey("speakers.id"))

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
    # owner_id = Column(Integer, ForeignKey("users.id"))
    session_image_url = Column(String, index=True)
    session_banner_url = Column(String, index=True)
    session_status_id = Column(Integer, ForeignKey("session_status.id"))
    is_archived = Column(Boolean, default=False)
    organization_id = Column(Integer, ForeignKey("organization.id"))

    conference = relationship("Conference", back_populates="sessions")
    # owner = relationship("User", back_populates="sessions")
    agenda = relationship("Agenda", secondary="agenda_session", back_populates="sessions")
    speakers = relationship("Speakers", secondary="session_speakers", back_populates="sessions")
    session_status = relationship("Sessionstatus", back_populates="session")
    session_documents = relationship("SessionDocuments", back_populates="session")
    organization = relationship("Organization", back_populates="sessions")

    @property
    def status(self):
        return self.session_status.status.upper()
    
class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    # owner_id = Column(Integer, ForeignKey("users.id"))
    body = Column(JSONB, index=True)

    conference = relationship("Conference", back_populates="settings")
    # owner = relationship("User", back_populates="settings")

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
    checked_in = Column(Boolean, default=False)

    user = relationship("User", back_populates="attendees")
    agenda = relationship("Agenda", back_populates="attendees")
    attendee_conference = relationship("Attendee_Conferences", back_populates="attendee")
    aitokens = relationship("AITokens", back_populates="attendee")
    attendee_exhibitors = relationship("AttendeeExhibitors", back_populates="attendee")
    
    _user_delegated_attrs = {"email", "first_name", "last_name", "company", "profile_image_url", "is_active"}

    def __getattr__(self, name):
        if name in self._user_delegated_attrs:
            return getattr(self.user, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
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
    sessions = relationship("Session", secondary="agenda_session", back_populates="agenda")

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
    organization_id = Column(Integer, ForeignKey("organization.id"))

    conference = relationship("Conference", back_populates="promotions")
    organization = relationship("Organization", back_populates="promotions")
    
    @property
    def location(self):
        return self.conference.location
    
    @property
    def conference_start_date(self):
        return self.conference.start_date
    
    @property
    def conference_end_date(self):
        return self.conference.end_date
    
    @property
    def event_id(self):
        return self.conference.uuid
    
    @property
    def conference_name(self):
        return self.conference.name
    
    @property
    def conference_image_url(self):
        return self.conference.conference_logo

class Sponsors(Base):
    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    # owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    description = Column(String, index=True)
    email = Column(String, index=True)
    contact_name = Column(String, index=True)
    contact_phone = Column(String, index=True)
    logo_image_url = Column(String, index=True)
    sponsorship_level = Column(String, index=True)
    is_archived = Column(Boolean, default=False)
    organization_id = Column(Integer, ForeignKey("organization.id"))

    # owner = relationship("User", back_populates="sponsors")
    event_sponsors = relationship("EventSponsors", back_populates="sponsors", overlaps="conference")
    conference = relationship("Conference", secondary="event_sponsors", back_populates="sponsors", overlaps="event_sponsors")
    organization = relationship("Organization", back_populates="sponsors")

class EventSponsors(Base):
    __tablename__ = "event_sponsors"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    sponsor_id = Column(Integer, ForeignKey("sponsors.id"))

    sponsors = relationship("Sponsors", back_populates="event_sponsors", overlaps="conference, sponsors")
    @property
    def spn_uuid(self):
        return self.sponsors.uuid
    
    _user_delegated_attrs = {"name", "description", "email", "contact_name", "contact_phone", "logo_image_url", "sponsorship_level", "is_archived"}
    
    def __getattr__(self, name):
        if name in self._user_delegated_attrs:
            return getattr(self.sponsors, name)
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    name = Column(String, index=True)
    location = Column(String, index=True)
    address = Column(String, index=True)
    geo_location = Column(String, index=True)
    is_archived = Column(Boolean, default=False)
    organization_id = Column(Integer, ForeignKey("organization.id"))

    conference = relationship("Conference", back_populates="venue")
    organization = relationship("Organization", back_populates="venues")
    
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

class EventDocuments(Base):
    __tablename__ = "event_documents"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    document_url = Column(String, index=True)
    content_type = Column(String, index=True)
    name = Column(String, index=True)
    size = Column(Float, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"))

    conference = relationship("Conference", back_populates="event_documents")
    organization = relationship("Organization", back_populates="event_documents")
    
    @property
    def conference_uuid(self):
        return self.conference.uuid
    
class SessionDocuments(Base):
    __tablename__ = "session_documents"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    document_url = Column(String, index=True)
    content_type = Column(String, index=True)
    name = Column(String, index=True)
    size = Column(Float, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"))

    session = relationship("Session", back_populates="session_documents")
    organization = relationship("Organization", back_populates="session_documents")
    
    @property
    def session_uuid(self):
        return self.session.uuid
    
class OrganizationSettings(Base):
    __tablename__ = "organization_settings"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"))
    event_brite_org_id = Column(String, index=True)
    event_brite_access_token = Column(String, index=True)

    organization = relationship("Organization", back_populates="organization_settings")
    
class Exhibitor(Base):
    __tablename__ = "exhibitor"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"))
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    about = Column(String, nullable=False)
    contact_name = Column(String, nullable=False)
    contact_phone = Column(String, nullable=False)
    contact_email = Column(String, nullable=False)
    booth_number = Column(String, nullable=False)
    category = Column(String, nullable=False)
    exhibitor_logo = Column(String)
    exhibitor_banner = Column(String)
    is_archived = Column(Boolean, default=False)
    
    organization = relationship("Organization", back_populates="exhibitors")
    event_exhibitor = relationship("EventExhibitor", back_populates="exhibitor", overlaps="conferences,exhibitors")
    exhibitor_documents = relationship("ExhibitorDocuments", back_populates="exhibitor")
    attendee_exhibitors = relationship("AttendeeExhibitors", back_populates="exhibitors")
    
class EventExhibitor(Base):
    __tablename__ = "event_exhibitor"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    exhibitor_id = Column(Integer, ForeignKey("exhibitor.id"))
    conference_id = Column(Integer, ForeignKey("conferences.id"))

    exhibitor = relationship("Exhibitor", back_populates="event_exhibitor", overlaps="conferences,exhibitors")
    
class ExhibitorDocuments(Base):
    __tablename__ = "exhibitor_documents"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    exhibitor_id = Column(Integer, ForeignKey("exhibitor.id"))
    document_url = Column(String, index=True)
    content_type = Column(String, index=True)
    name = Column(String, index=True)
    size = Column(Float, index=True)
    organization_id = Column(Integer, ForeignKey("organization.id"))

    exhibitor = relationship("Exhibitor", back_populates="exhibitor_documents")
    organization = relationship("Organization", back_populates="exhibitor_documents")
    
    @property
    def exhibitor_uuid(self):
        return self.exhibitor.uuid
    
class AttendeeExhibitors(Base):
    __tablename__ = "attendee_exhibitors"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime, index=True)
    updated_on = Column(DateTime, index=True)
    attendee_id = Column(Integer, ForeignKey("attendees.id"))
    exhibitor_id = Column(Integer, ForeignKey("exhibitor.id"))
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    
    attendee = relationship("Attendee", back_populates="attendee_exhibitors")
    exhibitors = relationship("Exhibitor", back_populates="attendee_exhibitors")
    conference = relationship("Conference", back_populates="attendee_exhibitors")