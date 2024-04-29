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
from ..static_enums.blob_container_enums import BlobContainer
from sqlalchemy.orm import joinedload

def get_sessions_by_organization_id(db: Session, organization_id: int, offset: int = 0, limit: int = 100):
    return db.query(models.Session).filter(models.Session.organization_id == organization_id, models.Session.is_archived == False).order_by(models.Session.updated_on.desc()).offset(offset).limit(limit).all()

def exclude_archived(session: models.Session):
    if session.speakers is not None:
        session.speakers = [speaker for speaker in session.speakers if not speaker.is_archived]

def add_speakers_to_session(db: Session, session: models.Session):
    db_session_speakers = db.query(models.SessionSpeakers).filter(models.SessionSpeakers.session_id == session.id).all()
    speaker_ids = [speaker.speaker_id for speaker in db_session_speakers]
    speakers = []
    for speaker_id in speaker_ids:
        speaker = db.query(models.Speakers).filter(models.Speakers.id == speaker_id, models.Speakers.is_archived == False).first()
        speakers.append(speaker)
    session.speakers_list = speakers
    return session

def get_sessions(db: Session, offset: int = 0, limit: int = 100):
    sessions = db.query(models.Session).options(joinedload(models.Session.speakers)).filter(models.Session.is_archived == False).order_by(models.Session.updated_on.desc()).offset(offset).limit(limit).all()
    for session in sessions:
        if session is not None:
            exclude_archived(session)
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
    db.commit()
    
    db_session.session_image_url = upload_image.get_actual_url(image_url=session.session_image_url, new_blob_container=BlobContainer.SESSION_IMAGES.value, new_blob_name=f"session-{db_session.uuid}") if session.session_image_url is not None else None
    
    db_session.session_banner_url = upload_image.get_actual_url(image_url=session.session_banner_url, new_blob_container=BlobContainer.SESSION_BANNERS.value, new_blob_name=f"session-{db_session.uuid}") if session.session_banner_url is not None else None
    
    try:
        db.commit()
    except Exception as e:
        db.delete(db_session)
        upload_image.delete_blob_by_url(db_session.session_image_url)
        upload_image.delete_blob_by_url(db_session.session_banner_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_session)
    db_session = db.query(models.Session).options(joinedload(models.Session.speakers)).filter(models.Session.id == db_session.id).first()
    exclude_archived(db_session)
    return db_session

def get_session_by_conference_uuid_session_uuid(db: Session, session_id: str, conference_id: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id, models.Conference.is_archived == False).first()
    if conference is None:
        return None
    db_session = db.query(models.Session).filter(models.Session.uuid == session_id, models.Session.conference_id == conference.id, models.Session.is_archived == False).first()
    if db_session is None:
        return None
    db_session = add_speakers_to_session(db, db_session)
    return db_session

def get_session_by_session_uuid(db: Session, uuid: str):
    db_session = db.query(models.Session).filter(models.Session.uuid == uuid, models.Session.is_archived == False).first()
    db_session = add_speakers_to_session(db, db_session)
    return db_session

def get_session_by_uuid_id(db: Session, uuid: int, owner_id: int):
    db_session = db.query(models.Session).filter(models.Session.uuid == uuid, models.Session.owner_id == owner_id, models.Session.is_archived == False).first()
    if db_session is not None:
        exclude_archived(db_session)
    return db_session

def get_all_sessions_by_uuid_id(db: Session, conference_uuid: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_uuid, models.Conference.is_archived == False).first()
    if conference is None:
        return None
    db_sessions = db.query(models.Session).options(joinedload(models.Session.speakers)).filter(models.Session.conference_id == conference.id, models.Session.is_archived == False).order_by(models.Session.updated_on.desc()).all()
    for db_session in db_sessions:
        if db_session is not None:
            exclude_archived(db_session)
    return db_sessions

def delete_session(db: Session, db_session: models.Session):
    if db_session.speakers and any([speaker.is_archived == False for speaker in db_session.speakers]):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Session is associated with a speaker. Cannot delete session.")
    db_session.is_archived = True
    db.commit()
    return True

def update_session_status(db_session, session_status):
    if session_status:
        db_session.session_status_id = session_enum.SessionEnum[session_status.upper()].value

def update_session_tags(session, session_dict):
    if session_dict.get('tags'):
        session_dict['tags'] = list(set(session.tags))

def update_session_fields(db_session, session_dict):
    non_nullable_fields = ['name','date','start_time','end_time','location','description']
    for key, value in session_dict.items():
        if key in non_nullable_fields and value is not None or key not in non_nullable_fields:
            setattr(db_session, key, value)

def validate_session_date(session, db_session):
    if session.date and (session.date < db_session.conference.start_date or session.date > db_session.conference.end_date or session.date < date.today()):
        logging.exception("Invalid date")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date")

def validate_session_time(session):
    if session.start_time and session.end_time and session.start_time > session.end_time:
        logging.exception("Invalid time")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid time")

def update_session_image_url(db_session: models.Session, session_image, blob_container):
    url_attribute = 'session_image_url' if blob_container == BlobContainer.SESSION_IMAGES.value else 'session_banner_url'
    current_url = getattr(db_session, url_attribute)

    if session_image is not None and upload_image.get_container_name_from_url(session_image) != blob_container:
        new_url = upload_image.get_actual_url(image_url=session_image, new_blob_container=blob_container, new_blob_name=f"session-{db_session.uuid}")
        setattr(db_session, url_attribute, new_url)
    elif session_image is None and current_url is not None:
        upload_image.delete_blob_by_url(current_url)
        setattr(db_session, url_attribute, None)
    
def update_session_speakers(db, db_session, speaker_ids):
    db.query(models.SessionSpeakers).filter(models.SessionSpeakers.session_id == db_session.id).delete()
    db.commit()
    for speaker_id in speaker_ids:
        session_speaker = models.SessionSpeakers(session_id=db_session.id, speaker_id=speaker_id, conference_id=db_session.conference_id)
        session_speaker.created_on = session_speaker.updated_on = datetime.utcnow()
        session_speaker.uuid = "ssp-" + str(uuid.uuid4())
        db.add(session_speaker)
    db.commit()

def update_session(db: Session, session: schemas.SessionUpdate, db_session: models.Session, speaker_ids: list[int]):
    session_dict = session.model_dump()
    session_status = session_dict.pop("status", None)
    session_image_url = session_dict.pop("session_image_url", None)
    session_banner_url = session_dict.pop("session_banner_url", None)
    session_dict.pop('id', None)
    session_dict.pop('conference_id', None)
    session_dict.pop('speakers', None)

    update_session_status(db_session, session_status)
    update_session_tags(session, session_dict)
    update_session_fields(db_session, session_dict)
    validate_session_date(session, db_session)
    validate_session_time(session)
    update_session_image_url(db_session, session_image_url, BlobContainer.SESSION_IMAGES.value)
    update_session_image_url(db_session, session_banner_url, BlobContainer.SESSION_BANNERS.value)

    db_session.updated_on = datetime.utcnow()
    try:
        db.commit()
    except Exception as e:
        if session_image_url:
            upload_image.delete_blob_by_url(db_session.session_image_url)
        if session_banner_url:
            upload_image.delete_blob_by_url(db_session.session_banner_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_session)

    update_session_speakers(db, db_session, speaker_ids)

    db_session = db.query(models.Session).options(joinedload(models.Session.speakers)).filter(models.Session.id == db_session.id).first()
    return db_session