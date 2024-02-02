from sqlalchemy.orm import Session
from .. import models, hashing
from ..schemas import user_schemas as schemas
from datetime import datetime
from . import agenda_crud
import uuid
from ..static_enums import organizer

def create_user(db: Session, user: schemas.UserCreate):
    user_dict = user.model_dump()
    user_status = user_dict.pop("status")
    db_user = models.User(**user_dict)
    db_user.user_status_id = organizer.OrganizerEnum[user_status.upper()].value
    db_user.hashed_password = hashing.get_password_hash(db_user.hashed_password)
    db_user.created_on = db_user.updated_on = datetime.utcnow()
    db_user.uuid = "usr-"+str(uuid.uuid4())
    db_user.role = "organizer"
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db_user.status = organizer.OrganizerEnum(db_user.user_status_id).name
    return db_user

def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    user.status = organizer.OrganizerEnum(user.user_status_id).name
    return user

def get_db_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email.ilike(email)).first()

def get_user_by_email_and_password(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email.ilike(email)).first()
    if user is None:
        return False
    if hashing.verify_password(password, user.hashed_password):
        return user
    return False

def get_users(db: Session, offset: int = 0, limit: int = 100):
    users = db.query(models.User).filter(models.User.role == 'organizer').offset(offset).limit(limit).all()
    for user in users:
        user.status = organizer.OrganizerEnum(user.user_status_id).name
    return users

def update_user(db: Session, user: schemas.UserBaseUpdate, db_user: models.User):
    user_dict = user.model_dump()
    user_status = user_dict.pop("status")
    
    if user_status is not None:
        db_user.user_status_id = organizer.OrganizerEnum[user_status.upper()].value
    
    non_nullable_fields = ['first_name','last_name','business_type']

    for key, value in user_dict.items():
        if key in non_nullable_fields:
            if value is not None:
                setattr(db_user, key, value)
        else:
            setattr(db_user, key, value)

    db_user.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    db_user.status = organizer.OrganizerEnum(db_user.user_status_id).name
    return db_user

def update_user_password(db: Session, user: schemas.UserPasswordUpdate, db_user: models.User):
    db_user.hashed_password = hashing.get_password_hash(user.new_password)
    db_user.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    db_user.status = organizer.OrganizerEnum(db_user.user_status_id).name
    return db_user

def update_user_password_by_email(db: Session, email: str, password: str):
    db_user = db.query(models.User).filter(models.User.email.ilike(email)).first()
    db_user.hashed_password = hashing.get_password_hash(password)
    db_user.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    db_user.status = organizer.OrganizerEnum(db_user.user_status_id).name
    return db_user

def delete_user(db: Session, user: models.User):
    db.query(models.Session).filter(models.Session.owner_id == user.id).delete()
    db.query(models.Settings).filter(models.Settings.owner_id == user.id).delete()
    conference = db.query(models.Conference).filter(models.Conference.owner_id == user.id).all()
    for c in conference:
        agenda_crud.delete_agenda_by_conference_id(db, conference_id=c.id)
    db.query(models.Conference).filter(models.Conference.owner_id == user.id).delete()
    db.delete(user)
    db.commit()
    return True