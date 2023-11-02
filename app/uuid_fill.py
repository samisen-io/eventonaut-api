from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .dependencies import get_db
from . import models
import uuid

router = APIRouter(tags=["uuid_fill"])

@router.put("/uuid_fill_users")
def uuid_fill_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    for user in users:
        user.uuid = str(uuid.uuid4())
    db.commit()
    return users

@router.put("/uuid_fill_conference")
def uuid_fill_conference(db: Session = Depends(get_db)):
    conferences = db.query(models.Conference).all()
    for conference in conferences:
        conference.uuid = str(uuid.uuid4())
    db.commit()
    return conferences

@router.put("/uuid_fill_session")
def uuid_fill_session(db: Session = Depends(get_db)):
    sessions = db.query(models.Session).all()
    for session in sessions:
        session.uuid = str(uuid.uuid4())
    db.commit()
    return sessions

@router.put("/uuid_fill_settings")
def uuid_fill_settings(db: Session = Depends(get_db)):
    settings = db.query(models.Settings).all()
    for setting in settings:
        setting.uuid = str(uuid.uuid4())
    db.commit()
    return settings

@router.put("/uuid_attendees")
def uuid_fill_attendees(db: Session = Depends(get_db)):
    attendees = db.query(models.Attendee).all()
    for attendee in attendees:
        attendee.uuid = str(uuid.uuid4())
    db.commit()
    return attendees

@router.put("/uuid_fill_agenda")
def uuid_fill_agenda(db: Session = Depends(get_db)):
    agendas = db.query(models.Agenda).all()
    for agenda in agendas:
        agenda.uuid = str(uuid.uuid4())
    db.commit()
    return agendas

@router.put("/uuid_fill_agenda_session")
def uuid_fill_agenda_session(db: Session = Depends(get_db)):
    agenda_sessions = db.query(models.AgendaSession).all()
    for agenda_session in agenda_sessions:
        agenda_session.uuid = str(uuid.uuid4())
    db.commit()
    return agenda_sessions
