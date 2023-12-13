from sqlalchemy.orm import Session
from ..models import Speakers, Conference
from ..schemas import speaker_schemas as schemas
import uuid
from datetime import datetime

def get_speaker_by_name(db: Session, name: str):
    return db.query(Speakers).filter(Speakers.name.ilike(name)).first()

def create_speaker(db: Session, speaker: schemas.SpeakerCreate):
    conference = db.query(Conference).filter(Conference.uuid == speaker.conference_id).first()
    speaker.model_dump().pop("conference_id")
    db_speaker = Speakers(**speaker.model_dump())
    db_speaker.uuid = "spk-" + str(uuid.uuid4())
    db_speaker.created_on = datetime.utcnow()
    db_speaker.updated_on = datetime.utcnow()
    db_speaker.conference_id = conference.id
    db.add(db_speaker)
    db.commit()
    db.refresh(db_speaker)
    return db_speaker

def get_all_speakers(db: Session, offset: int = 0, limit: int = 100):
    return db.query(Speakers).offset(offset).limit(limit).all()

def get_speaker(db: Session, speaker_id: uuid):
    return db.query(Speakers).filter(Speakers.uuid == speaker_id).first()

def update_speaker(db: Session, speaker: schemas.SpeakerUpdate):
    db_speaker = db.query(Speakers).filter(Speakers.uuid == speaker.id).first()
    speaker_dict = speaker.model_dump()
    speaker_dict.pop("id")
    speaker_conference_id = speaker.conference_id or None
    conference = db.query(Conference).filter(Conference.uuid == speaker_conference_id).first()
    db_speaker.conference_id = conference.id if conference else None
    speaker_dict.pop("conference_id")
    for field, value in speaker_dict.items():
        if value is not None:
            setattr(db_speaker, field, value)
    db_speaker.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_speaker)
    return db_speaker


def delete_speaker(db: Session, speaker_id: str):
    db_speaker = db.query(Speakers).filter(Speakers.uuid == speaker_id).first()
    db.delete(db_speaker)
    db.commit()
    return True