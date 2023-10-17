from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, JSON,DATE
from sqlalchemy.orm import relationship
from pytz import timezone

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    account_type = Column(String, index=True)
    bussiness_type = Column(String, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    conferences = relationship("Conference", back_populates="owner")

#class to create conference table and add relationship to session table
class Conference(Base):
    __tablename__ = "conferences"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String, index=True)
    start_date = Column(DATE, index=True)
    end_date = Column(DATE, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="conferences")
    sessions = relationship("Session", back_populates="conference")
    settings = relationship("Settings", back_populates="conference")

# class to define session table
class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    start_time = Column(String, index=True)
    end_time = Column(String, index=True)
    description = Column(String, index=True)
    date = Column(String, index=True) 
    location = Column(String, index=True)
    conference_id = Column(Integer, ForeignKey("conferences.id"))

    conference = relationship("Conference", back_populates="sessions")

#class to define settings table with id, conference id as foreign key, created on and updated on as datetime and body as a string
class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    conference_id = Column(Integer, ForeignKey("conferences.id"))
    tz = timezone('Asia/Kolkata')
    created_on = Column(DateTime)
    updated_on = Column(DateTime)
    body = Column(JSON, index=True)

    conference = relationship("Conference", back_populates="settings")