from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, date, time
from .. import models
from ..schemas import session_schemas as schemas
from pytz import timezone
import uuid

#get all sessions
def get_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Session).offset(skip).limit(limit).all()

def create_conference_session(db: Session, session: schemas.SessionCreate, owner_id: int):
    db_session = models.Session(**session.model_dump())
    tz = timezone('Asia/Kolkata')
    db_session.created_on = datetime.now(tz)
    db_session.updated_on = datetime.now(tz)
    db_session.owner_id = owner_id
    db_session.uuid = str(uuid.uuid4())
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session(db: Session, session_id: int):
    return db.query(models.Session).filter(models.Session.id == session_id).first()

# get sessions by owner id and session id
def get_session_by_uuid_id(db: Session, uuid: int, owner_id: int):
    return db.query(models.Session).filter(models.Session.uuid == uuid, models.Session.owner_id == owner_id).first()

#get sessions by conference_id
def get_all_sessions_by_uuid_id(db: Session, uuid: str):
    conference_id = db.query(models.Conference).filter(models.Conference.uuid == uuid).first().id
    return db.query(models.Session).filter(models.Session.conference_id == conference_id).all()


#delete session
def delete_session(db: Session, uuid: str, owner_id: int):
    db.query(models.Session).filter(models.Session.uuid == uuid,models.Session.owner_id == owner_id).delete()
    db.commit()
    return True

# delete all sessions with conference id
def delete_all_sessions_by_conference_id(db: Session, conference_id: int):
    db.query(models.Session).filter(models.Session.conference_id == conference_id).delete()
    db.commit()
    return True

#update session
def update_session(db: Session, session: schemas.SessionUpdate, uuid: str, owner_id: int):
    db_session = db.query(models.Session).filter(models.Session.uuid == uuid,models.Session.owner_id == owner_id).first()
    tz = timezone('Asia/Kolkata')
    db_session.name = session.name
    db_session.date = session.date
    db_session.start_time = session.start_time
    db_session.end_time = session.end_time
    db_session.location = session.location
    db_session.description = session.description
    db_session.updated_on = datetime.now(tz)
    db.commit()
    db.refresh(db_session)
    return db_session