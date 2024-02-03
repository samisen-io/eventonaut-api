import logging
import os
from urllib.parse import urlparse
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.routers import upload_image
from ..models import Speakers, Conference
from ..schemas import speaker_schemas as schemas
import uuid
from .. import models
from datetime import datetime
import random

def get_speaker_by_email(db: Session, email: str, owner_id: int):
    return db.query(Speakers).filter(Speakers.email.ilike(email), Speakers.owner_id == owner_id, Speakers.isarchived == False).first()

def get_speaker_by_uuid(db: Session, uuid: str, owner_id: int):
    return db.query(Speakers).filter(Speakers.uuid == uuid, Speakers.owner_id == owner_id, Speakers.isarchived == False).first()

def get_speakers_by_owner_id(db: Session, owner_id: int, offset: int = 0, limit: int = 100):
    return db.query(Speakers).filter(Speakers.owner_id == owner_id, Speakers.isarchived == False).offset(offset).limit(limit).all()

def create_speaker(db: Session, speaker: schemas.SpeakerCreate):
    conference = db.query(Conference).filter(Conference.uuid == speaker.conference_id).first()
    db_speaker = Speakers(**speaker.model_dump())
    db_speaker.uuid = "spk-" + str(uuid.uuid4())
    db_speaker.created_on = datetime.utcnow()
    db_speaker.updated_on = datetime.utcnow()
    db_speaker.conference_id = conference.id
    
    if speaker.profile_image_url is not None:
        parsed_url = parsed_url = urlparse(speaker.profile_image_url)
        path = parsed_url.path
        filename_with_ext = os.path.basename(path)
        _, extension = os.path.splitext(filename_with_ext)

        if extension not in ['.jpg', '.jpeg', '.png']:
            logging.exception("Invalid image file format")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file format")
        
        image_url = upload_image.move_file_from_temporary_to_permanent_container(source_container_name="temporary-images", dest_container_name="speaker-images", old_blob_name=filename_with_ext, new_blob_name=f"speaker-{db_speaker.uuid}" + extension)
    
    db_speaker.profile_image_url = image_url
    
    db.add(db_speaker)
    try:
        db.commit()
    except Exception as e:
        upload_image.delete_blob("speaker-images", f"speaker-{db_speaker.uuid}" + extension)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_speaker)
    return db_speaker

def get_all_speakers(db: Session, offset: int = 0, limit: int = 100):
    return db.query(Speakers).offset(offset).limit(limit).all()

def get_speaker(db: Session, speaker_id: uuid):
    return db.query(Speakers).filter(Speakers.uuid == speaker_id, Speakers.isarchived == False).first()

def get_speakers_by_conference_id_owner_id(db: Session, conference_id: str, owner_id: int):
    conference = db.query(Conference).filter(Conference.uuid == conference_id, Conference.owner_id == owner_id, Conference.isarchived == False).first()
    if conference is None:
        return None
    conference_id = conference.id if conference else None
    speaker_ids = [speaker.speaker_id for speaker in db.query(models.SessionSpeakers).filter(models.SessionSpeakers.conference_id == conference_id).all()]
    db_speakers = db.query(Speakers).filter(Speakers.id.in_(speaker_ids)).all()
    return db_speakers

def get_speakers_by_conference_id(db: Session, conference_uuid: str):
    conference = db.query(Conference).filter(Conference.uuid == conference_uuid).first()
    conference_id = conference.id if conference else None
    return db.query(Speakers).filter(Speakers.conference_id == conference_id).all()

def update_speaker(db: Session, speaker: schemas.SpeakerUpdate):
    db_speaker = db.query(Speakers).filter(Speakers.uuid == speaker.id).first()
    speaker_dict = speaker.model_dump()
    speaker_dict.pop("id")
    speaker_conference_id = speaker.conference_id or None
    conference = db.query(Conference).filter(Conference.uuid == speaker_conference_id).first()
    db_speaker.conference_id = conference.id if conference else None
    speaker_dict.pop("conference_id")
    for key, value in speaker_dict.items():
        if value is not None:
            setattr(db_speaker, key, value)
            
    if speaker.profile_image_url is not None:
        parsed_url = parsed_url = urlparse(speaker.profile_image_url)
        path = parsed_url.path
        filename_with_ext = os.path.basename(path)
        _, extension = os.path.splitext(filename_with_ext)

        if extension not in ['.jpg', '.jpeg', '.png']:
            logging.exception("Invalid image file format")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file format")
        
        image_url = upload_image.move_file_from_temporary_to_permanent_container(source_container_name="temporary-images", dest_container_name="speaker-images", old_blob_name=filename_with_ext, new_blob_name=f"speaker-{db_speaker.uuid}" + extension)
        db_speaker.profile_image_url = image_url
    
    db_speaker.updated_on = datetime.utcnow()
    try:
        db.commit()
    except Exception as e:
        if speaker.profile_image_url is not None:
            upload_image.delete_blob("speaker-images", f"speaker-{db_speaker.uuid}" + extension)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_speaker)
    return db_speaker

def delete_speaker(db: Session, speaker_id: str):
    db_speaker = db.query(Speakers).filter(Speakers.uuid == speaker_id).first()
    db_speaker.isarchived = True
    db.commit()
    return True