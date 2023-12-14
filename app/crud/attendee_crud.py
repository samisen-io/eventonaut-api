from sqlalchemy.orm import Session
from .. import models
from ..schemas import attendee_schemas as schemas, attendee_conference_schemas, thread_schemas, session_schemas, conference_schemas
from datetime import datetime
from .. import hashing
from .. AI_assitant import create_thread, delete_thread
import uuid

# create attendee
def create_attendee(db: Session, attendee: schemas.AttendeeCreate):
    db_user = models.User(**attendee.model_dump())
    db_user.hashed_password = hashing.get_password_hash(db_user.hashed_password)
    db_user.created_on = datetime.utcnow()
    db_user.updated_on = datetime.utcnow()
    db_user.uuid = "usr-" + str(uuid.uuid4())
    db_user.role = "attendee"
    db_user.is_active = True
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

    attendee = schemas.Attendee(uuid=db_attendee.uuid, email=db_user.email, first_name=db_user.first_name, last_name=db_user.last_name, title=db_attendee.title, company=db_user.company, bio=db_attendee.bio, share_my_profile=db_attendee.share_my_profile, share_my_agenda=db_attendee.share_my_agenda, profile_image_url=db_attendee.profile_image_url, thread_id=db_attendee.thread_id,is_active=db_user.is_active)
    return attendee

def get_thread_id_by_attendee_id(db: Session, attendee_id: int):
    db_attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    if db_attendee is None:
        return None
    return db_attendee.thread_id

# get all attendees
def get_attendees(db: Session, skip: int = 0, limit: int = 100):
    db_attendees = db.query(models.Attendee).offset(skip).limit(limit).all()
    if db_attendees is None or len(db_attendees) == 0:
        return None
    attendees = []
    for db_attendee in db_attendees:
        user = db.query(models.User).filter(models.User.id == db_attendee.user_id).first()
        if user is not None:
            attendees.append(schemas.Attendee(uuid=db_attendee.uuid, email=user.email, first_name=user.first_name, last_name=user.last_name, title=db_attendee.title, company=user.company, bio=db_attendee.bio, share_my_profile=db_attendee.share_my_profile, share_my_agenda=db_attendee.share_my_agenda, profile_image_url=db_attendee.profile_image_url, thread_id=db_attendee.thread_id,is_active=user.is_active))
    return attendees

# get attendee by email
def get_attendee_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# get attendee by id
def get_attendee_by_uuid(db: Session, attendee_id: str):
    db_attendee = db.query(models.Attendee).filter(models.Attendee.uuid == attendee_id).first()
    if db_attendee is None:
        return None
    db_user = db.query(models.User).filter(models.User.id == db_attendee.user_id).first()
    if db_user is None:
        return None
    attendee = schemas.Attendee(uuid=db_attendee.uuid, email=db_user.email, first_name=db_user.first_name, last_name=db_user.last_name, title=db_attendee.title, company=db_user.company, bio=db_attendee.bio, share_my_profile=db_attendee.share_my_profile, share_my_agenda=db_attendee.share_my_agenda, profile_image_url=db_attendee.profile_image_url, thread_id=db_attendee.thread_id,is_active=db_user.is_active)
    return attendee

def get_attendee_by_id(db: Session, attendee_id: int):
    db_attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    if db_attendee is None:
        return None
    db_user = db.query(models.User).filter(models.User.id == db_attendee.user_id).first()
    if db_user is None:
        return None
    attendee = schemas.Attendee(uuid=db_attendee.uuid, email=db_user.email, first_name=db_user.first_name, last_name=db_user.last_name, title=db_attendee.title, company=db_user.company, bio=db_attendee.bio, share_my_profile=db_attendee.share_my_profile, share_my_agenda=db_attendee.share_my_agenda, profile_image_url=db_attendee.profile_image_url, thread_id=db_attendee.thread_id,is_active=db_user.is_active)
    return attendee

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
        'share_my_agenda': attendee.share_my_agenda
    }

    for key, value in updates_user.items():
        if value == "":
            setattr(db_user, key, "None")
        elif value is not None:
            setattr(db_user, key, value)

    for key, value in updates_attendee.items():
        if value == "":
            setattr(db_attendee, key, "None")
        elif value is not None:
            setattr(db_attendee, key, value)

    db_attendee.updated_on = datetime.utcnow()
    db_user.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_attendee)
    db.refresh(db_user)
    attendee = schemas.Attendee(uuid=db_attendee.uuid, email=db_user.email, first_name=db_user.first_name, last_name=db_user.last_name, title=db_attendee.title, company=db_user.company, bio=db_attendee.bio, share_my_profile=db_attendee.share_my_profile, share_my_agenda=db_attendee.share_my_agenda, profile_image_url=db_attendee.profile_image_url, thread_id=db_attendee.thread_id,is_active=db_user.is_active)
    return attendee

def update_attendee_image_url(db: Session, attendee_id: int, image_url: str):
    db_attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    db_attendee.profile_image_url = image_url
    db_attendee.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_attendee)
    return db_attendee

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
    attendee = schemas.Attendee(uuid=db_attendee.uuid, email=db_user.email, first_name=db_user.first_name, last_name=db_user.last_name, title=db_attendee.title, company=db_user.company, bio=db_attendee.bio, share_my_profile=db_attendee.share_my_profile, share_my_agenda=db_attendee.share_my_agenda, profile_image_url=db_attendee.profile_image_url, thread_id=db_attendee.thread_id,is_active=db_user.is_active)
    return attendee

# delete attendee by id
def delete_attendee_by_uuid(db: Session, attendee_id: int):
    db_attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    db_user = db.query(models.User).filter(models.User.id == db_attendee.user_id).first()
    if db_attendee.thread_id != "None" and db_attendee.thread_id is not None:
        delete_thread(db_attendee.thread_id)
    db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.attendee_id == db_attendee.id).delete()
    db.query(models.Agenda).filter(models.Agenda.attendee_id == db_attendee.id).delete()
    db.query(models.AgendaSession).filter(models.AgendaSession.attendee_id == db_attendee.id).delete()
    db.delete(db_attendee)
    db.delete(db_user)
    db.commit()
    return True

# create attendee conference
def create_attendee_conference(db: Session, attendee_id: int, attendee_conference):
    attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    try:
        conference = db.query(models.Conference).filter(models.Conference.code == attendee_conference.conference_code).first()
    except:
        conference = db.query(models.Conference).filter(models.Conference.uuid == attendee_conference.conference_id).first()
    db_attendee_conference = models.Attendee_Conferences(attendee_id=attendee.id, conference_id=conference.id)
    db_attendee_conference.uuid = "ate-" + str(uuid.uuid4())
    db_attendee_conference.created_on = datetime.utcnow()
    db_attendee_conference.updated_on = datetime.utcnow()
    db.add(db_attendee_conference)
    db.commit()
    db.refresh(db_attendee_conference)
    conf_schema = {
        "id":conference.uuid, 
        "name":conference.name, 
        "location":conference.location, 
        "start_date":conference.start_date,
        "end_date":conference.end_date,
        "description":conference.description,
        "conference_logo":conference.conference_logo
    }
    attendee_conf = attendee_conference_schemas.AttendeeConference(uuid=db_attendee_conference.uuid, attendee_id=attendee.uuid, conference=conf_schema)
    return attendee_conf

# get attendee conference by attendee id and conference id
def get_attendee_conference_by_attendee_id_and_conference_id(db: Session, attendee_id: int, conference_id: str):
    attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id).first()
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
        conferences.append(db.query(models.Conference).filter(models.Conference.id == attendee_conference.conference_id).first())
    return conferences

# delete attendee conference by attendee id and conference id
def delete_attendee_conference_by_attendee_id_and_conference_id(db: Session, attendee_id: int, conference_code: str):
    attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    conference_id = db.query(models.Conference).filter(models.Conference.code == conference_code).first().id
    db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.attendee_id == attendee.id, models.Attendee_Conferences.conference_id == conference_id).delete()
    db.commit()
    return True

def get_all_attendee_profiles_by_conference_id(db: Session, conference_id: str):
    conference_id = db.query(models.Conference).filter(models.Conference.uuid == conference_id).first().id
    attendee_conferences = db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.conference_id == conference_id).all()
    attendees = []
    for attendee_conference in attendee_conferences:
        attendee = db.query(models.Attendee).filter(models.Attendee.id == attendee_conference.attendee_id).first()
        user = db.query(models.User).filter(models.User.id == attendee.user_id).first()
        attendees.append(schemas.Attendee(uuid=attendee.uuid, email=user.email, first_name=user.first_name, last_name=user.last_name, title=attendee.title, company=user.company, bio=attendee.bio, share_my_profile=attendee.share_my_profile, share_my_agenda=attendee.share_my_agenda, profile_image_url=attendee.profile_image_url, thread_id=attendee.thread_id,is_active=user.is_active))
    return attendees