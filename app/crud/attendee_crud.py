from sqlalchemy.orm import Session
from pytz import timezone
from .. import models
from ..schemas import attendee_schemas as schemas
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
    db_attendee.thread_id = create_thread().id
    db_attendee.is_active = True
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
    }

    for key, value in updates.items():
        if value is not None:
            setattr(db_attendee, key, value)

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
