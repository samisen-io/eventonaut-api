from sqlalchemy.orm import Session
from datetime import datetime, date
from .. import models
from ..schemas import session_schemas as schemas
from fastapi import HTTPException, status
import logging
import uuid

def get_sessions(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.Session).offset(offset).limit(limit).all()

def create_conference_session(db: Session, session: schemas.SessionCreate, owner_id: int, conference_id: int):
    db_session = models.Session(name=session.name, start_time=session.start_time, end_time=session.end_time, description=session.description, date=session.date, location=session.location, owner_id=owner_id, session_image_url=session.session_image_url)
    db_session.created_on = db_session.updated_on = datetime.utcnow()
    db_session.uuid = "ses-" + str(uuid.uuid4())
    db_session.owner_id = owner_id
    db_session.conference_id = conference_id
    db_session.speakers = session.speakers
    db_session.tags = session.tags
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session_by_conference_uuid_session_uuid(db: Session, session_id: str, conference_id: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id).first()
    return db.query(models.Session).filter(models.Session.uuid == session_id, models.Session.conference_id == conference.id).first()

def get_session_by_session_uuid(db: Session, uuid: str):
    return db.query(models.Session).filter(models.Session.uuid == uuid).first()

def get_session_by_uuid_id(db: Session, uuid: int, owner_id: int):
    return db.query(models.Session).filter(models.Session.uuid == uuid, models.Session.owner_id == owner_id).first()

def get_all_sessions_by_uuid_id(db: Session, conference_uuid: str):
    conference_id = db.query(models.Conference).filter(models.Conference.uuid == conference_uuid).first().id
    db_sessions=db.query(models.Session).filter(models.Session.conference_id == conference_id).all()
    return db_sessions

def delete_session(db: Session, db_session: models.Session):
    db.query(models.AgendaSession).filter(models.AgendaSession.session_id == db_session.id).delete()
    db.delete(db_session)
    db.commit()
    return True

def update_session(db: Session, session: schemas.SessionUpdate, db_session: models.Session):
    session_dict = session.model_dump()
    session_dict.pop('id')
    session_dict.pop('conference_id')

    if session_dict['speakers'] is not None:
        speakers:list[str] = []
        for speaker in session.speakers:
            if speaker not in speakers:
                speakers.append(speaker)
        session_dict['speakers'] = speakers
    
    if session_dict['tags'] is not None:
        tags:list[str] = []
        for tag in session.tags:
            if tag not in tags:
                tags.append(tag)
        session_dict['tags'] = tags

    non_nullable_fields = ['name','date','start_time','end_time','location','description','speakers','tags']
    
    for key, value in session_dict.items():
        if key in non_nullable_fields:
            if value is not None:
                setattr(db_session, key, value)
        else:
            setattr(db_session, key, value)

    if session.date is not None and (session.date < db_session.conference.start_date or session.date > db_session.conference.end_date or session.date < date.today()):
        logging.exception("Invalid date")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date")
    
    if session.start_time is not None and session.end_time is not None and session.start_time > session.end_time:
        logging.exception("Invalid time")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid time")

    db_session.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_session)
    return db_session