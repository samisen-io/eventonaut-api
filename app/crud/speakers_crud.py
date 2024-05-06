import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.routers import upload_image
from ..models import Speakers, Conference
from ..schemas import speaker_schemas as schemas
import uuid
from .. import models
from datetime import datetime
from ..static_enums.blob_container_enums import BlobContainer
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import aliased

# def get_speakers_by_organization_id(db: Session, organization_id: int, offset: int = 0, limit: int = 100):
#     return db.query(Speakers).filter(Speakers.organization_id == organization_id, Speakers.is_archived == False).order_by(Speakers.updated_on.desc()).offset(offset).limit(limit).all()

def exclude_archived(speaker: Speakers):
    if speaker.sessions is not None:
        speaker.sessions = [session for session in speaker.sessions if not session.is_archived]

def get_speaker_by_email(db: Session, email: str, organization_id: int):
    return db.query(Speakers).filter(Speakers.email.ilike(email), Speakers.organization_id == organization_id, Speakers.is_archived == False).first()

def get_speaker_by_uuid(db: Session, uuid: str, organization_id: int):
    speaker = db.query(Speakers).filter(Speakers.uuid == uuid, Speakers.organization_id == organization_id, Speakers.is_archived == False).first()
    if speaker is not None:
        exclude_archived(speaker)
    return speaker

def get_speakers_by_organization_id(db: Session, organization_id: int, offset: int = 0, limit: int = 100):
    speakers = db.query(Speakers).filter(Speakers.organization_id == organization_id, Speakers.is_archived == False).order_by(Speakers.updated_on.desc()).offset(offset).limit(limit).all()
    for speaker in speakers:
        if speaker is not None:
            exclude_archived(speaker)
    return speakers

def create_speaker(db: Session, speaker: schemas.SpeakerCreate, organization_id: int, session_ids: list[int]):
    speaker_dict = speaker.model_dump()
    speaker_dict.pop("sessions")
    db_speaker = Speakers(**speaker_dict)
    db_speaker.uuid = "spk-" + str(uuid.uuid4())
    db_speaker.created_on = datetime.utcnow()
    db_speaker.updated_on = datetime.utcnow()
    db_speaker.organization_id = organization_id
    
    db_speaker.profile_image_url = upload_image.get_actual_url(image_url=speaker.profile_image_url, new_blob_container=BlobContainer.SPEAKER_IMAGES.value, new_blob_name=f"speaker-{db_speaker.uuid}") if speaker.profile_image_url is not None else None
    
    db.add(db_speaker)
    try:
        db.commit()
    except Exception as e:
        upload_image.delete_blob_by_url(db_speaker.profile_image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    for session_id in session_ids:
        conference_id = db.query(models.Session).filter(models.Session.id == session_id).first().conference_id
        session_speaker = models.SessionSpeakers(session_id=session_id, speaker_id=db_speaker.id, conference_id=conference_id)
        session_speaker.uuid = "ssp-" + str(uuid.uuid4())
        session_speaker.created_on = session_speaker.updated_on = datetime.utcnow()
        db.add(session_speaker)
    db.commit()
    db.refresh(db_speaker)
    return db_speaker

def get_all_speakers(db: Session, offset: int = 0, limit: int = 100):
    return db.query(Speakers).options(joinedload(Speakers.sessions)).filter(Speakers.is_archived == False).order_by(Speakers.updated_on.desc()).offset(offset).limit(limit).all()

def get_speaker(db: Session, speaker_id: uuid):
    speaker = db.query(Speakers).filter(Speakers.uuid == speaker_id, Speakers.is_archived == False).first()
    if speaker is not None:
        exclude_archived(speaker)
    return speaker

def get_speakers_by_conference_id_organization_id(db: Session, conference_id: int, organization_id: int):
    speakers = db.query(Speakers).join(models.SessionSpeakers, models.SessionSpeakers.speaker_id == Speakers.id).filter(models.SessionSpeakers.conference_id == conference_id, Speakers.organization_id == organization_id, Speakers.is_archived == False).order_by(models.Speakers.updated_on.desc()).all()
    for speaker in speakers:
        if speaker is not None:
            exclude_archived(speaker)
    return speakers

def get_speakers_by_session_uuid(db: Session, session_uuid: str):
    session = db.query(models.Session).filter(models.Session.uuid == session_uuid).first()
    session_id = session.id if session else None
    speaker_ids = [speaker.speaker_id for speaker in db.query(models.SessionSpeakers).filter(models.SessionSpeakers.session_id == session_id).all()]
    return db.query(Speakers).filter(Speakers.id.in_(speaker_ids)).order_by(models.Speakers.updated_on.desc()).all()

def get_speaker_uuid_by_email(db: Session, email: str):
    speaker = db.query(Speakers).filter(Speakers.email == email).first()
    return speaker.uuid if speaker else None

def update_speaker(db: Session, speaker: schemas.SpeakerUpdate, db_speaker: Speakers, session_ids: list[int]):
    speaker_dict = speaker.model_dump()
    speaker_dict.pop("id")
    speaker_dict.pop("sessions")
    profile_image_url = speaker_dict.pop("profile_image_url")
    
    non_nullable_fields = ["name", "email"]
    
    for key, value in speaker_dict.items():
        if key in non_nullable_fields and value is not None:
            setattr(db_speaker, key, value)
        elif key not in non_nullable_fields:
            setattr(db_speaker, key, value)
            
    if profile_image_url is not None and upload_image.get_container_name_from_url(profile_image_url) != BlobContainer.SPEAKER_IMAGES.value:
        db_speaker.profile_image_url = upload_image.get_actual_url(image_url=profile_image_url, new_blob_container=BlobContainer.SPEAKER_IMAGES.value, new_blob_name=f"speaker-{db_speaker.uuid}")
    elif profile_image_url is None and db_speaker.profile_image_url is not None:
        upload_image.delete_blob_by_url(db_speaker.profile_image_url)
        db_speaker.profile_image_url = None
    
    db_speaker.updated_on = datetime.utcnow()
    try:
        db.commit()
    except Exception as e:
        if speaker.profile_image_url is not None:
            upload_image.delete_blob_by_url(db_speaker.profile_image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.query(models.SessionSpeakers).filter(models.SessionSpeakers.speaker_id == db_speaker.id).delete()
    db.commit()
    for session_id in session_ids:
        conference_id = db.query(models.Session).filter(models.Session.id == session_id).first().conference_id
        session_speaker = models.SessionSpeakers(session_id=session_id, speaker_id=db_speaker.id, conference_id=conference_id)
        session_speaker.uuid = "ssp-" + str(uuid.uuid4())
        session_speaker.created_on = session_speaker.updated_on = datetime.utcnow()
        db.add(session_speaker)
        db.commit()
        db.refresh(session_speaker)
    return db_speaker

def delete_speaker(db: Session, speaker_id: str):
    db_speaker = db.query(Speakers).filter(Speakers.uuid == speaker_id).first()
    
    if db_speaker.sessions and any([session.is_archived == False for session in db_speaker.sessions]):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Speaker is associated with a session. Cannot delete speaker.")
    
    db_speaker.is_archived = True
    db.commit()
    return True