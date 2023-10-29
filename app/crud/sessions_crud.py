from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, date, time
from .. import models
from ..schemas import session_schemas as schemas
from .. encryption import encrypt_number, decrypt_number
from pytz import timezone

#crud for session
def get_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Session).offset(skip).limit(limit).all()

def create_conference_session(db: Session, session: schemas.SessionCreate, owner_id: int):
    db_session = models.Session(**session.model_dump())
    tz = timezone('Asia/Kolkata')
    db_session.created_on = datetime.now(tz)
    db_session.updated_on = datetime.now(tz)
    db_session.conference_id = decrypt_number(session.conference_id)
    db_session.owner_id = owner_id
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session(db: Session, session_id: int):
    return db.query(models.Session).filter(models.Session.id == session_id).first()

# get sessions by owner id and session id
def get_session_by_owner_id(db: Session, session_id: int, owner_id: int):
    return db.query(models.Session).filter(models.Session.id == session_id, models.Session.owner_id == owner_id).first()

def get_sessions_by_name(db: Session, conference_id:int, name: str):
    return db.query(models.Session).filter(models.Session.conference_id == conference_id, models.Session.name == name).all()

def get_sessions_by_date(db: Session, conference_id:int, date: date):
    return db.query(models.Session).filter(models.Session.conference_id==conference_id, models.Session.date==date, models.Session.date == date).all()

# get all sessions by conference_id and start time and compare only hours and minutes
def get_sessions_by_start_time(db: Session, conference_id:int, start_time: time):
    return db.query(models.Session).filter(models.Session.conference_id==conference_id, models.Session.start_time == start_time).all()

def get_sessions_by_end_time(db: Session, conference_id:int, end_time: time):
    return db.query(models.Session).filter(models.Session.conference_id==conference_id, models.Session.end_time == end_time).all()

def get_sessions_by_location(db: Session, conference_id:int, location: str):
    return db.query(models.Session).filter(models.Session.conference_id==conference_id, models.Session.location == location).all()

def get_sessions_by_description(db: Session, conference_id: int, description: str):
    return db.query(models.Session).filter(models.Session.conference_id==conference_id, models.Session.description == description).all()

#get sessions by conference_id
def get_all_sessions_by_conference_id(db: Session, conference_id: int):
    return db.query(models.Session).filter(models.Session.conference_id == conference_id).all()

# get sessions by conference_id and range of date
def get_all_sessions_by_conference_id_between_date(db: Session, conference_id: int, filter_start_date: date, filter_end_date: date):
    return db.query(models.Session).filter(models.Session.conference_id == conference_id, models.Session.date >= filter_start_date, models.Session.date <= filter_end_date).all()

# get all conferences based on name or description strings
def get_all_sessions_by_search(db: Session,conference_id:int, search_string: str):
    return db.query(models.Session).filter(models.Session.conference_id == conference_id, or_(models.Session.name.ilike('%'+search_string+'%'), models.Session.description.ilike('%'+search_string+'%'), models.Session.date.ilike('%'+search_string+'%'), models.Session.location.ilike('%'+search_string+'%'))).all()

#delete session
def delete_session(db: Session, session_id: int, owner_id: int):
    db.query(models.Session).filter(models.Session.id == session_id,models.Session.owner_id == owner_id).delete()
    db.commit()
    return True

# delete all sessions with conference id
def delete_all_sessions_by_conference_id(db: Session, conference_id: int):
    db.query(models.Session).filter(models.Session.conference_id == conference_id).delete()
    db.commit()
    return True

#update session
def update_session(db: Session, session: schemas.SessionUpdate, session_id: int, owner_id: int):
    db_session = db.query(models.Session).filter(models.Session.id == session_id,models.Session.owner_id == owner_id).first()
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