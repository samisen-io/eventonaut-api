import os
from urllib.parse import urlparse
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.routers import upload_image
from .. import models
from ..schemas import session_schemas as schemas
from fastapi import HTTPException, status
import logging
import uuid
from ..static_enums import session as session_enum

def add_speakers_to_session(db: Session, session: models.Session):
    db_session_speakers = db.query(models.SessionSpeakers).filter(models.SessionSpeakers.session_id == session.id).all()
    speaker_ids = [speaker.speaker_id for speaker in db_session_speakers]
    speakers = []
    for speaker_id in speaker_ids:
        speaker = db.query(models.Speakers).filter(models.Speakers.id == speaker_id).first()
        speakers.append(speaker)
    session.speakers_list = speakers
    return session

def get_sessions(db: Session, offset: int = 0, limit: int = 100):
    sessions = db.query(models.Session).offset(offset).limit(limit).all()
    for session in sessions:
        session = add_speakers_to_session(db, session)
        session.status = session_enum.SessionEnum(session.session_status_id).name
    return sessions

def create_conference_session(db: Session, session: schemas.SessionCreate, owner_id: int, conference_id: int, speaker_ids: list[int]):
    db_session = models.Session(name=session.name, start_time=session.start_time, end_time=session.end_time, description=session.description, date=session.date, location=session.location, owner_id=owner_id, session_image_url=session.session_image_url)
    db_session.created_on = db_session.updated_on = datetime.utcnow()
    db_session.uuid = "ses-" + str(uuid.uuid4())
    db_session.owner_id = owner_id
    db_session.conference_id = conference_id
    db_session.tags = session.tags
    db_session.session_status_id = session_enum.SessionEnum[session.status.upper()].value
    db.add(db_session)
    db.commit()
    for speaker_id in speaker_ids:
        session_speaker = models.SessionSpeakers(session_id=db_session.id, speaker_id=speaker_id, conference_id=conference_id)
        session_speaker.uuid = "ssp-" + str(uuid.uuid4())
        session_speaker.created_on = session_speaker.updated_on = datetime.utcnow()
        db.add(session_speaker)
    
    
    db_session.session_image_url = upload_image.get_actual_url(image_url=session.session_image_url, new_blob_container="session-images", new_blob_name=f"session-{db_session.uuid}") if session.session_image_url is not None else None
    
    try:
        db.commit()
    except Exception as e:
        upload_image.delete_blob_by_url(db_session.session_image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_session)
    db_session = add_speakers_to_session(db, db_session)
    db_session.status = session_enum.SessionEnum(db_session.session_status_id).name
    return db_session

def get_session_by_conference_uuid_session_uuid(db: Session, session_id: str, conference_id: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id, models.Conference.is_archived == False).first()
    if conference is None:
        return None
    db_session = db.query(models.Session).filter(models.Session.uuid == session_id, models.Session.conference_id == conference.id, models.Session.is_archived == False).first()
    if db_session is None:
        return None
    db_session = add_speakers_to_session(db, db_session)
    db_session.status = session_enum.SessionEnum(db_session.session_status_id).name
    return db_session

def get_session_by_session_uuid(db: Session, uuid: str):
    db_session = db.query(models.Session).filter(models.Session.uuid == uuid, models.Session.is_archived == False).first()
    db_session = add_speakers_to_session(db, db_session)
    return db_session

def get_session_by_uuid_id(db: Session, uuid: int, owner_id: int):
    db_session = db.query(models.Session).filter(models.Session.uuid == uuid, models.Session.owner_id == owner_id, models.Session.is_archived == False).first()
    return db_session

def get_all_sessions_by_uuid_id(db: Session, conference_uuid: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_uuid, models.Conference.is_archived == False).first()
    if conference is None:
        return None
    db_sessions = db.query(models.Session).filter(models.Session.conference_id == conference.id, models.Session.is_archived == False).all()
    for db_session in db_sessions:
        db_session = add_speakers_to_session(db, db_session)
        db_session.status = session_enum.SessionEnum(db_session.session_status_id).name
    return db_sessions

def delete_session(db: Session, db_session: models.Session):
    db_session.is_archived = True
    db.commit()
    return True

def update_session(db: Session, session: schemas.SessionUpdate, db_session: models.Session, speaker_ids: list[int]):
    session_dict = session.model_dump()
    session_dict.pop('id')
    session_dict.pop('conference_id')
    session_status = session_dict.pop("status")
    session_image_url = session_dict.pop("session_image_url")
    
    if session_status is not None:
        db_session.session_status_id = session_enum.SessionEnum[session_status.upper()].value

    if session_dict['tags'] is not None:
        tags:list[str] = []
        for tag in session.tags:
            if tag not in tags:
                tags.append(tag)
        session_dict['tags'] = tags

    non_nullable_fields = ['name','date','start_time','end_time','location','description','tags']
    
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

    if session_image_url is not None:
        db_session.session_image_url = upload_image.get_actual_url(image_url=session_image_url, new_blob_container="session-images", new_blob_name=f"session-{db_session.uuid}") 
    elif session_image_url is None and db_session.session_image_url is not None:
        upload_image.delete_blob("session-images", f"session-{db_session.uuid}")
        db_session.session_image_url = None

    db_session.updated_on = datetime.utcnow()
    try:
        db.commit()
    except Exception as e:
        if session_image_url is not None:
            upload_image.delete_blob_by_url(db_session.session_image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_session)
    db.query(models.SessionSpeakers).filter(models.SessionSpeakers.session_id == db_session.id).delete()
    db.commit()

    for speaker_id in speaker_ids:
        session_speaker = models.SessionSpeakers(session_id=db_session.id, speaker_id=speaker_id, conference_id=db_session.conference_id)
        session_speaker.created_on = session_speaker.updated_on = datetime.utcnow()
        db.add(session_speaker)
    db.commit()

    db_session = add_speakers_to_session(db, db_session)
    db_session.status = session_enum.SessionEnum(db_session.session_status_id).name
    return db_session