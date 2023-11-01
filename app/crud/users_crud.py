from sqlalchemy.orm import Session
from .. import models, hashing
from ..schemas import user_schemas as schemas
from datetime import datetime
from pytz import timezone


# create user
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.model_dump())
    tz = timezone('Asia/Kolkata')
    db_user.hashed_password = hashing.get_password_hash(db_user.hashed_password)
    db_user.created_on = datetime.now(tz)
    db_user.updated_on = datetime.now(tz)
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
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

# update user
def update_user(db: Session, user: schemas.UserBaseUpdate, user_id: int):
    tz = timezone('Asia/Kolkata')
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if user.email is not None and user.email.strip() != "" and user.email != "string":
        db_user.email = user.email
    if user.first_name is not None and user.first_name.strip() != "" and user.first_name != "string":
        db_user.first_name = user.first_name
    if user.last_name is not None and user.last_name.strip() != "" and user.last_name != "string":
        db_user.last_name = user.last_name
    if user.account_type is not None and user.account_type.strip() != "" and user.account_type != "string":
        db_user.account_type = user.account_type
    if user.bussiness_type is not None and user.bussiness_type.strip() != "" and user.bussiness_type != "string":
        db_user.bussiness_type = user.bussiness_type
    db_user.updated_on = datetime.now(tz)
    db.commit()
    db.refresh(db_user)
    return db_user

# update password
def update_user_password(db: Session, user: schemas.UserPassword, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    tz=timezone('Asia/Kolkata')
    db_user.hashed_password = hashing.get_password_hash(user.hashed_password)
    db_user.updated_on = datetime.now(tz)
    db.commit()
    db.refresh(db_user)
    return db_user

# delete user
def delete_user(db: Session, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.query(models.Conference).filter(models.Conference.owner_id == user_id).delete()
    db.query(models.Session).filter(models.Session.owner_id == user_id).delete()
    db.query(models.Settings).filter(models.Settings.owner_id == user_id).delete()
    db.commit()
    return True