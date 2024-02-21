import os
from sqlalchemy.orm import Session
from .. import models
from ..schemas import attendee_schemas as schemas, attendee_conference_schemas, thread_schemas
from datetime import datetime
from .. import hashing
from .. AI_assitant import create_thread, delete_thread
import uuid
from ..crud import conferences_crud
from ..static_enums import event
from ..static_enums import attendee as attendee_enum
from urllib.parse import urlparse
from ..routers import upload_image
from fastapi import HTTPException, status
import logging
from ..static_enums.blob_container_enums import BlobContainer
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import joinedload

# create attendee
def create_attendee(db: Session, attendee: schemas.AttendeeCreate):
    attendee_dict = attendee.model_dump()
    attendee_status = attendee_dict.pop("status", None)
    db_user = models.User(**attendee_dict)
    db_user.hashed_password = hashing.get_password_hash(db_user.hashed_password)
    db_user.created_on = datetime.utcnow()
    db_user.updated_on = datetime.utcnow()
    db_user.uuid = "usr-" + str(uuid.uuid4())
    db_user.role = "attendee"
    db_user.is_active = True
    db_user.user_status_id = attendee_enum.AttendeeEnum[attendee_status.upper()].value if attendee_status is not None else attendee_enum.AttendeeEnum.INACTIVE.value
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    db_attendee = models.Attendee()
    db_attendee.created_on = datetime.utcnow()
    db_attendee.updated_on = datetime.utcnow()
    db_attendee.uuid = "atd-" + str(uuid.uuid4())
    db_attendee.user_id = db_user.id
    db_attendee.thread_id = create_thread(thread_schemas.Thread()).id
    db.add(db_attendee)
    db.commit()
    db.refresh(db_attendee)
    attendee = db.query(models.Attendee).options(joinedload(models.Attendee.user)).filter(models.Attendee.user_id == db_user.id).first()
    return attendee

def get_thread_id_by_attendee_id(db: Session, attendee_id: int):
    db_attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    if db_attendee is None:
        return None
    return db_attendee.thread_id

# get all attendees
def get_attendees(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Attendee).options(joinedload(models.Attendee.user)).offset(skip).limit(limit).all()

# get attendee by email
def get_attendee_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email, models.User.is_archived == False).first()

# get attendee by id
def get_attendee_by_uuid(db: Session, attendee_id: str):
    return db.query(models.Attendee).options(joinedload(models.Attendee.user)).filter(models.Attendee.uuid == attendee_id, models.User.is_archived == False).first()


def get_attendee_by_id(db: Session, attendee_id: int):
    return db.query(models.Attendee).options(joinedload(models.Attendee.user)).filter(models.Attendee.user_id == attendee_id, models.User.is_archived == False).first()

# update attendee by id
def update_attendee_by_uuid(db: Session, attendee_id: int, attendee: schemas.AttendeeUpdate):
    db_attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    db_user = db.query(models.User).filter(models.User.id == db_attendee.user_id).first()
    if db_attendee is None or db_user is None:
        return None
    updates_user = {
        'company': attendee.company,
        'first_name': attendee.first_name,
        'last_name': attendee.last_name,
    }

    updates_attendee = {
        'title': attendee.title,
        'bio': attendee.bio,
        'share_my_profile': attendee.share_my_profile,
        'share_my_agenda': attendee.share_my_agenda,
    }

    for key, value in updates_user.items():
        setattr(db_user, key, value)

    for key, value in updates_attendee.items():
        setattr(db_attendee, key, value)
        
    if attendee.status is not None:
        db_user.user_status_id = attendee_enum.AttendeeEnum[attendee.status.upper()].value

    if attendee.profile_image_url is not None and upload_image.get_container_name_from_url(attendee.profile_image_url) != BlobContainer.ATTENDE_PROFILE_IMAGES.value:
        db_user.profile_image_url = upload_image.get_actual_url(image_url=attendee.profile_image_url, new_blob_container=BlobContainer.ATTENDE_PROFILE_IMAGES.value, new_blob_name=f"profile-{db_attendee.uuid}")
    elif attendee.profile_image_url is None and db_user.profile_image_url is not None:
        upload_image.delete_blob_by_url(db_user.profile_image_url)
        db_user.profile_image_url = None

    db_attendee.updated_on = datetime.utcnow()
    db_user.updated_on = datetime.utcnow()
    try:
        db.commit()
    except Exception as e:
        if attendee.profile_image_url is not None:
            upload_image.delete_blob_by_url(db_user.profile_image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_attendee)
    db.refresh(db_user)
    attendee = db.query(models.Attendee).options(joinedload(models.Attendee.user)).filter(models.Attendee.user_id == db_user.id).first()
    return attendee

# update attendee password by id
def update_attendee_password_by_uuid(db: Session, attendee_id: int, attendee: schemas.AttendePassword):
    db_attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    db_user = db.query(models.User).filter(models.User.id == db_attendee.user_id).first()
    if db_attendee is None or db_user is None:
        return None
    if not hashing.verify_password(attendee.old_password, db_user.hashed_password):
        return None
    db_user.hashed_password = hashing.get_password_hash(attendee.new_password)
    db_user.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    attendee = db.query(models.Attendee).options(joinedload(models.Attendee.user)).filter(models.Attendee.user_id == db_user.id).first()
    return attendee

# delete attendee by id
def delete_attendee_by_uuid(db: Session, attendee_id: int):
    db_attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    db_user = db.query(models.User).filter(models.User.id == db_attendee.user_id, models.User.is_archived == False).first()
    db_user.is_archived = True
    db.commit()
    return True

# create attendee conference
def create_attendee_conference(db: Session, attendee_id: int, attendee_conference: attendee_conference_schemas.AttendeeConferenceCreate):
    attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    if len(attendee_conference.conference_identifier) == 6:
        conference = db.query(models.Conference).filter(models.Conference.code == attendee_conference.conference_identifier).first()
    else:
        conference = db.query(models.Conference).filter(models.Conference.uuid == attendee_conference.conference_identifier).first()
    db_attendee_conference = models.Attendee_Conferences(attendee_id=attendee.id, conference_id=conference.id)
    db_attendee_conference.uuid = "ate-" + str(uuid.uuid4())
    db_attendee_conference.created_on = db_attendee_conference.updated_on = datetime.utcnow()
    db.add(db_attendee_conference)
    db.commit()
    db.refresh(db_attendee_conference)
    db.refresh(conference)
    attendee_conf = attendee_conference_schemas.AttendeeConference(uuid=db_attendee_conference.uuid, attendee_id=attendee.uuid, conference_id=conference.uuid)
    return attendee_conf

# get attendee conference by attendee id and conference id
def get_attendee_conference_by_attendee_id_and_conference_id(db: Session, attendee_id: int, conference_id: str):
    attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id, models.Conference.is_archived == False).first()
    if attendee is None or conference is None:
        return None
    return db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.attendee_id == attendee.id).filter(models.Attendee_Conferences.conference_id == conference.id).first()

# get all attendee conferences
def get_all_attendee_conferences(db: Session, attendee_id: int, skip: int = 0, limit: int = 100):
    attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    attendee_conferences = db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.attendee_id == attendee.id).offset(skip).limit(limit).all()
    if attendee_conferences is None:
        return None
    conferences = []
    for attendee_conference in attendee_conferences:
        conference = db.query(models.Conference).options(joinedload(models.Conference.client),joinedload(models.Conference.venue),joinedload(models.Conference.sponsors)).filter(models.Conference.id == attendee_conference.conference_id, models.Conference.is_archived == False, models.Conference.end_date >= datetime.utcnow()).first()
        if conference is None:
            continue
        conference.__dict__.pop('client_id')
        conferences.append(conference)
    return conferences

# delete attendee conference by attendee id and conference id
def delete_attendee_conference_by_attendee_id_and_conference_id(db: Session, attendee_conference: attendee_conference_schemas.AttendeeConference):
    db.delete(attendee_conference)
    db.commit()
    return True

def get_all_attendee_profiles_by_conference_id(db: Session, conference_id: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id, models.Conference.is_archived == False).first()
    if conference is None:
        return None
    conference_id = conference.id
    attendee_conferences = db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.conference_id == conference_id).all()
    return db.query(models.Attendee).options(joinedload(models.Attendee.user)).filter(models.Attendee.id.in_([attendee_conference.attendee_id for attendee_conference in attendee_conferences])).all()