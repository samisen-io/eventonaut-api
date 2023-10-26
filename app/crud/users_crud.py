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

# get all users by first_name
def get_users_by_first_name(db: Session, first_name: str):
    return db.query(models.User).filter(models.User.first_name == first_name).all()

# get all users by last_name
def get_users_by_last_name(db: Session, last_name: str):
    return db.query(models.User).filter(models.User.last_name == last_name).all()

# get user by account_type
def get_users_by_account_type(db: Session, account_type: str):
    return db.query(models.User).filter(models.User.account_type == account_type).all()

# get user by bussiness_type
def get_users_by_bussiness_type(db: Session, bussiness_type: str):
    return db.query(models.User).filter(models.User.bussiness_type == bussiness_type).all()

# update user
def update_user(db: Session, user: schemas.UserBase, user_id: int):
    tz = timezone('Asia/Kolkata')
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.email = user.email
    db_user.first_name = user.first_name
    db_user.last_name = user.last_name
    db_user.account_type = user.account_type
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