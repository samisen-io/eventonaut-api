from sqlalchemy.orm import Session
from pytz import timezone
from .. import models
from ..schemas import attendee_schemas as schemas, attendee_conference_schemas, thread_schemas, session_schemas
from datetime import datetime
from .. import hashing
from .. AI_assitant import create_thread
import uuid

# create attendee
def create_attendee(db: Session, attendee: schemas.AttendeeCreate):
    db_attendee = models.Attendee(**attendee.model_dump())
    db_attendee.hashed_password = hashing.get_password_hash(db_attendee.hashed_password)
    tz = timezone('Asia/Kolkata')
    db_attendee.created_on = datetime.now(tz)
    db_attendee.updated_on = datetime.now(tz)
    db_attendee.uuid = str(uuid.uuid4())
    db_attendee.thread_id = create_thread(thread_schemas.Thread).id
    db_attendee.is_active = True
    if attendee.profile_image_url is None or attendee.profile_image_url.strip() == "" or attendee.profile_image_url == "string" or attendee.profile_image_url == "None":
        attendee.profile_image_url = "None"
    db.add(db_attendee)
    db.commit()
    db.refresh(db_attendee)
    return db_attendee

# get all attendees
def get_attendees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Attendee).offset(skip).limit(limit).all()

# get attendee by email
def get_attendee_by_email(db: Session, email: str):
    return db.query(models.Attendee).filter(models.Attendee.email == email).first()

# get attendee by id
def get_attendee_by_uuid(db: Session, attendee_id: str):
    return db.query(models.Attendee).filter(models.Attendee.uuid == attendee_id).first()

# update attendee by id
def update_attendee_by_uuid(db: Session, attendee_id: str, attendee: schemas.AttendeeBase):
    db_attendee = db.query(models.Attendee).filter(models.Attendee.uuid == attendee_id).first()
    db_attendee.updated_on = datetime.now(timezone('Asia/Kolkata'))

    updates = {
        "first_name": attendee.first_name,
        "last_name": attendee.last_name,
        "email": attendee.email,
        "profile_image_url": attendee.profile_image_url if attendee.profile_image_url is not None else "None"
    }

    for key, value in updates.items():
        if value is not None:
            setattr(db_attendee, key, value)

    if attendee.profile_image_url is None or attendee.profile_image_url.strip() == "" or attendee.profile_image_url == "string" or attendee.profile_image_url == "None":
        attendee.profile_image_url = "None"

    db.commit()
    db.refresh(db_attendee)
    return db_attendee

# update attendee password by id
def update_attendee_password_by_uuid(db: Session, attendee_id: str, attendee: schemas.AttendePassword):
    db_attendee = db.query(models.Attendee).filter(models.Attendee.uuid == attendee_id).first()
    db_attendee.hashed_password = hashing.get_password_hash(attendee.hashed_password)
    db_attendee.updated_on = datetime.now(timezone('Asia/Kolkata'))
    db.commit()
    db.refresh(db_attendee)
    return db_attendee

# delete attendee by id
def delete_attendee_by_uuid(db: Session, attendee_id: str):
    db.query(models.Attendee).filter(models.Attendee.uuid == attendee_id).delete()
    db.commit()
    return True

# create attendee conference
def create_attendee_conference(db: Session, attendee_conference: attendee_conference_schemas.AttendeeConferenceCreate):
    attendee_id = db.query(models.Attendee).filter(models.Attendee.uuid == attendee_conference.attendee_id).first().id
    conference_id = db.query(models.Conference).filter(models.Conference.code == attendee_conference.conference_code).first().id
    db_attendee_conference = models.Attendee_Conferences(attendee_id=attendee_id, conference_id=conference_id)
    db_attendee_conference.uuid = str(uuid.uuid4())
    tz = timezone('Asia/Kolkata')
    db_attendee_conference.created_on = datetime.now(tz)
    db_attendee_conference.updated_on = datetime.now(tz)
    db.add(db_attendee_conference)
    db.commit()
    db.refresh(db_attendee_conference)
    conf_list = []
    for conf in db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.attendee_id == attendee_id).all():
        conf_uuid = db.query(models.Conference).filter(models.Conference.id == conf.conference_id).first().uuid
        conf_list.append(conf_uuid)
    attendee_conf = attendee_conference_schemas.AttendeeConference(uuid=db_attendee_conference.uuid, attendee_id=attendee_conference.attendee_id, conference_id=conf_list)
    return attendee_conf

# get attendee conference by attendee id and conference id
def get_attendee_conference_by_attendee_id_and_conference_id(db: Session, attendee_id: str, conference_id: str):
    attendee_id = db.query(models.Attendee).filter(models.Attendee.uuid == attendee_id).first().id
    conference_id = db.query(models.Conference).filter(models.Conference.uuid == conference_id).first().id
    return db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.attendee_id == attendee_id).filter(models.Attendee_Conferences.conference_id == conference_id).first()

# get all attendee conferences
def get_all_attendee_conferences(db: Session, attendee_id: str, skip: int = 0, limit: int = 100):
    attendee_id = db.query(models.Attendee).filter(models.Attendee.uuid == attendee_id).first().id
    attendee_conferences = db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.attendee_id == attendee_id).offset(skip).limit(limit).all()
    conferences = []
    for attendee_conference in attendee_conferences:
        conferences.append(db.query(models.Conference).filter(models.Conference.id == attendee_conference.conference_id).first())
    return conferences

# delete attendee conference by attendee id and conference id
def delete_attendee_conference_by_attendee_id_and_conference_id(db: Session, attendee_id: str, conference_code: str):
    attendee_id = db.query(models.Attendee).filter(models.Attendee.uuid == attendee_id).first().id
    conference_id = db.query(models.Conference).filter(models.Conference.code == conference_code).first().id
    db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.attendee_id == attendee_id,models.Attendee_Conferences.conference_id == conference_id).delete()
    db.commit()
    return True

def get_all_attendee_profiles_by_conference_id(db: Session, conference_id: str):
    conference_id = db.query(models.Conference).filter(models.Conference.uuid == conference_id).first().id
    attendee_conferences = db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.conference_id == conference_id).all()
    attendees = []
    for attendee_conference in attendee_conferences:
        attendees.append(db.query(models.Attendee).filter(models.Attendee.id == attendee_conference.attendee_id,models.Attendee.share_my_profile == True).first())
    return attendees