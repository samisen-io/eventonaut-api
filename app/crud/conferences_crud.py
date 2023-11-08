from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from .. import models
from ..schemas import conference_schemas as schemas
from . import agenda_crud
from pytz import timezone
import uuid

# get all conferences
def get_conferences(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Conference).offset(skip).limit(limit).all()

def get_conferences_by_owner_id(db: Session, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.owner_id == owner_id).all()

# create conference
def create_user_conference(db: Session, conference: schemas.ConferenceCreate, user_id: int):
    db_conference = models.Conference(**conference.model_dump(), owner_id=user_id)
    if conference.description is None:
        db_conference.description = "None"
    if conference.conference_logo is None:
        db_conference.conference_logo = "None"
    tz = timezone('Asia/Kolkata')
    db_conference.created_on = datetime.now(tz)
    db_conference.updated_on = datetime.now(tz)
    db_conference.uuid = str(uuid.uuid4())
    db.add(db_conference)
    db.commit()
    db.refresh(db_conference)
    return db_conference

# get conference by uuid and owner id
def get_conference_by_uuid(db: Session, uuid: str, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.uuid == uuid, models.Conference.owner_id == owner_id).first()

def get_conference_by_conference_uuid(db: Session, uuid: str):
    return db.query(models.Conference).filter(models.Conference.uuid == uuid).first()

# delete conference by conference id
def delete_conference(db: Session, owner_id: int, uuid: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == uuid, models.Conference.owner_id == owner_id).first()
    if conference is None:
        return False
    sessions = db.query(models.Session).filter(models.Session.conference_id == conference.id, models.Session.owner_id == owner_id)
    for session in sessions:
        db.delete(session)
    db.query(models.Settings).filter(models.Settings.conference_id == conference.id, models.Settings.owner_id == owner_id).delete()
    agenda_crud.delete_agenda_by_conference_id(db, conference_id=conference.id)
    db.delete(conference)
    db.commit()
    return True

# update conference by conference id
def update_user_conference(db: Session, conference: schemas.ConferenceCreate, uuid: str, owner_id:int):
    db_conference = db.query(models.Conference).filter(models.Conference.uuid == uuid,models.Conference.owner_id == owner_id).first()
    tz = timezone('Asia/Kolkata')

    updates = {
        'name': conference.name,
        'location': conference.location,
        'start_date': conference.start_date,
        'end_date': conference.end_date,
        'description': conference.description if conference.description is not None else "None"
    }

    for key, value in updates.items():
        if value is not None:
            setattr(db_conference, key, value)

    if conference.start_date is not None and conference.end_date is not None:
        if conference.start_date > conference.end_date or conference.start_date < date.today():
            raise HTTPException(status_code=400, detail="Invalid date range")

    db_conference.updated_on = datetime.now(tz)
    db.commit()
    db.refresh(db_conference)
    return db_conference
