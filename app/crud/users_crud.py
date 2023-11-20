from sqlalchemy.orm import Session
from .. import models, hashing
from ..schemas import user_schemas as schemas
from datetime import datetime
from pytz import timezone
from . import agenda_crud
import uuid

# create user
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.model_dump())
    tz = timezone('Asia/Kolkata')
    db_user.hashed_password = hashing.get_password_hash(db_user.hashed_password)
    db_user.created_on = datetime.now(tz)
    db_user.updated_on = datetime.now(tz)
    if user.company is None or user.company == "string" or user.company == "None" or user.company.strip() == "":
        db_user.company = "None"
    db_user.uuid = str(uuid.uuid4())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# get user by id
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

# get user by email ignore case
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email.ilike(email)).first()

# get user by email and password
def get_user_by_email_and_password(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email.ilike(email)).first()
    if user is None:
        return False
    if hashing.verify_password(password, user.hashed_password):
        return user
    return False

# get all users
def get_users(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.User).offset(offset).limit(limit).all()

# update user
def update_user(db: Session, user: schemas.UserBaseUpdate, user_id: int):
    tz = timezone('Asia/Kolkata')
    db_user = db.query(models.User).filter(models.User.id == user_id).first()


    updates = {
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'company': user.company,
        'bussiness_type': user.bussiness_type
    }
    
    for key, value in updates.items():
        if value is not None:
            setattr(db_user, key, value)

    if user.company is None or user.company == "string" or user.company == "None" or user.company.strip() == "":
        db_user.company = "None"


    db_user.updated_on = datetime.now(tz)
    db.commit()
    db.refresh(db_user)
    return db_user

# update password
def update_user_password(db: Session, user: schemas.UserPasswordUpdate, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    tz=timezone('Asia/Kolkata')
    db_user.hashed_password = hashing.get_password_hash(user.new_password)
    db_user.updated_on = datetime.now(tz)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password_by_email(db: Session, email: str, password: str):
    db_user = db.query(models.User).filter(models.User.email.ilike(email)).first()
    tz=timezone('Asia/Kolkata')
    db_user.hashed_password = hashing.get_password_hash(password)
    db_user.updated_on = datetime.now(tz)
    db.commit()
    db.refresh(db_user)
    return db_user

# delete user
def delete_user(db: Session, user_id: int):
    db.query(models.Session).filter(models.Session.owner_id == user_id).delete()
    db.query(models.Settings).filter(models.Settings.owner_id == user_id).delete()
    conference = db.query(models.Conference).filter(models.Conference.owner_id == user_id).all()
    for c in conference:
        agenda_crud.delete_agenda_by_conference_id(db, conference_id=c.id)
    db.query(models.Conference).filter(models.Conference.owner_id == user_id).delete()
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return True