from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime, date, time
from .. import models
from ..schemas import session_schemas as schemas
from fastapi import HTTPException
from typing import List
from pytz import timezone

#get all sessions
def get_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Session).offset(skip).limit(limit).all()

def create_conference_session(db: Session, session: schemas.SessionCreate, owner_id: int):
    db_session = models.Session(name=session.name, start_time=session.start_time, end_time=session.end_time, description=session.description, date=session.date, location=session.location, owner_id=owner_id)
    conference_id = db.query(models.Conference).filter(models.Conference.uuid == session.conference_id).first().id
    tz = timezone('Asia/Kolkata')
    db_session.created_on = datetime.now(tz)
    db_session.updated_on = datetime.now(tz)
    db_session.owner_id = owner_id
    db_session.conference_id = conference_id
    db_session.speakers = session.speakers
    db_session.tags = session.tags
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
def get_all_sessions_by_uuid_id(db: Session, conference_uuid: str) -> List[schemas.Session]:
    conference_id = db.query(models.Conference).filter(models.Conference.uuid == conference_uuid).first().id
    db_sessions=db.query(models.Session).filter(models.Session.conference_id == conference_id).all()
    return [schemas.Session(**db_session.__dict__) for db_session in db_sessions]

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
    
    speakers:list[str] = []
    tags:list[str] = []

    if session.speakers is not None:
        for speaker in session.speakers:
            if speaker is None or speaker == "" or speaker == "string":
                raise HTTPException(status_code=400, detail="Invalid speaker")
            if speaker not in speakers:
                speakers.append(speaker)
    else:
        speakers = db_session.speakers
    
    if session.tags is not None:
        for tag in session.tags:
            if tag is None or tag == "" or tag == "string":
                raise HTTPException(status_code=400, detail="Invalid tag")
            if tag not in tags:
                tags.append(tag)
    else:
        tags = db_session.tags

    updates = {
        'name': session.name,
        'date': session.date,
        'start_time': session.start_time,
        'end_time': session.end_time,
        'location': session.location,
        'description': session.description,
        'speakers': speakers,
        'tags': tags
    }
    
    for key, value in updates.items():
        if value is not None:
            setattr(db_session, key, value)

    if session.date < db_session.conference.start_date or session.date > db_session.conference.end_date or session.date < date.today():
        raise HTTPException(status_code=400, detail="Invalid date")
    
    if session.start_time > session.end_time:
        raise HTTPException(status_code=400, detail="Invalid time")

    db_session.updated_on = datetime.now(tz)
    db.commit()
    db.refresh(db_session)
    return db_session