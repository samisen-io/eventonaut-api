from sqlalchemy.orm import Session
from ..models import Speakers, Conference
from ..schemas import speaker_schemas as schemas
import uuid
from .. import models
from datetime import datetime
import random

def get_speaker_by_name(db: Session, name: str):
    return db.query(Speakers).filter(Speakers.name.ilike(name)).first()

def get_speaker_by_uuid(db: Session, uuid: str, owner_id: int):
    return db.query(Speakers).filter(Speakers.uuid == uuid, Speakers.owner_id == owner_id).first()

def get_speakers_by_owner_id(db: Session, owner_id: int, offset: int = 0, limit: int = 100):
    return db.query(Speakers).filter(Speakers.owner_id == owner_id).offset(offset).limit(limit).all()

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

def get_speakers_by_conference_id_owner_id(db: Session, conference_id: str, owner_id: int):
    conference = db.query(Conference).filter(Conference.uuid == conference_id).first()
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
    db_speaker.profile_image_url = speaker_dict.pop("profile_image_url")
    for key, value in speaker_dict.items():
        if value is not None:
            setattr(db_speaker, key, value)
    db_speaker.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_speaker)
    return db_speaker

def delete_speaker(db: Session, speaker_id: str):
    db_speaker = db.query(Speakers).filter(Speakers.uuid == speaker_id).first()
    db.delete(db_speaker)
    db.commit()
    return True

# def fill_the_db(db: Session):
#     db_sessions = db.query(models.Session).all()

#     for session in db_sessions:
#         db_owner_id = session.owner_id

#         owner_conferences = db.query(models.Conference).filter(models.Conference.owner_id == db_owner_id).all()

#         conference_ids = [conference.id for conference in owner_conferences]

#         session.conference_id = random.choice(conference_ids)
#         db.commit()
#         db.refresh(session)

#     return True


#     for conference in db_confereces:
#         db_conf_spk = db.query(models.Speakers).filter(models.Speakers.owner_id == conference.owner_id).all()
#         db_sessions = db.query(models.Session).filter(models.Session.conference_id == conference.id).all()

#         if (db_sessions is None and len(db_sessions) == 0) or (db_conf_spk is None and len(db_conf_spk) == 0):
#             continue

#         spk_ids = [spk.id for spk in db_conf_spk]

#         range = -1

#         for session in db_sessions:
#             range += 1
#             if range >= len(spk_ids):
#                 range = 0
#             session_speaker = models.SessionSpeakers(session_id=session.id, speaker_id=spk_ids[range], conference_id=conference.id)
#             session_speaker.created_on = session_speaker.updated_on = datetime.utcnow()
#             db.add(session_speaker)
#             db.commit()
#             db.refresh(session_speaker)

#     # db_speakers = db.query(Speakers).all()
#     # db_users = db.query(models.User).filter(models.User.role == 'organizer').all()
    

#     # db_user_list = []

#     # for db_user in db_users:
#     #     db_confereces = db.query(models.Conference).filter(models.Conference.owner_id == db_user.id).first()
#     #     if db_confereces is not None:
#     #         db_user_list.append(db_user.id)

#     # range = -1

#     # for db_speaker in db_speakers:
#     #     range += 1
#     #     if range >= len(db_user_list):
#     #         range = 0
#     #     db_speaker.owner_id = db_user_list[range]
#     #     db.commit()
#     #     db.refresh(db_speaker)


#     # non_conferences_ids = []
#     # for db_speaker in db_speakers:
#     #     db_confereces = db.query(Conference).filter(Conference.owner_id == db_speaker.owner_id).all()
#     #     for conference in db_confereces:
#     #         db_sessions = db.query(models.Session).filter(models.Session.conference_id == conference.id).all()
#     #         if db_sessions is not None and len(db_sessions) > 0:
#     #             non_conferences_ids.append(conference.id)

#     # for db_speaker in db_speakers:
#     #     if db_speaker.conference_id is None:
#     #         db_speaker.conference_id = random.choice(non_conferences_ids)
#     #         db.commit()
#     #         db.refresh(db_speaker)
#     return True