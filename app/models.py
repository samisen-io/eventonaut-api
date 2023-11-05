from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, DATE, TIME, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import uuid

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    account_type = Column(String, index=True)
    bussiness_type = Column(String, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    conferences = relationship("Conference", back_populates="owner")
    sessions = relationship("Session", back_populates="owner")
    settings = relationship("Settings", back_populates="owner")

#class to create conference table and add relationship to session table
class Conference(Base):
    __tablename__ = "conferences"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String, index=True, unique=True)
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    name = Column(String, index=True)
    location = Column(String, index=True)
    start_date = Column(DATE, index=True)
    end_date = Column(DATE, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="conferences")
    sessions = relationship("Session", back_populates="conference")
    settings = relationship("Settings", back_populates="conference")
    agenda = relationship("Agenda", back_populates="conference")

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
    speakers = Column(ARRAY(String), index=True)
    tags = Column(ARRAY(String), index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    conference = relationship("Conference", back_populates="sessions")
    owner = relationship("User", back_populates="sessions")
    agenda_session = relationship("AgendaSession", back_populates="session")

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
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, index=True)
    hashed_password = Column(String, index=True)
    is_active = Column(Boolean, default=True)

    agenda = relationship("Agenda", back_populates="attendees")
    agenda_session = relationship("AgendaSession", back_populates="attendees")

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