from sqlalchemy.orm import Session
from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = "fakehashedpassword"
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#function to delete user
def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db.delete(db_user)
    db.commit()
    return db_user

#functions for conferences
def get_conference(db: Session, conference_id: int):
    return db.query(models.Conference).filter(models.Conference.id == conference_id).first()

#function to get all conferences
def get_conferences(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Conference).offset(skip).limit(limit).all()

#function to create conference
def create_conference(db: Session, conference: schemas.ConferenceCreate):
    db_conference = models.Conference(title=conference.title, description=conference.description, start_date=conference.start_date, end_date=conference.end_date, owner_id=conference.owner_id)
    db.add(db_conference)
    db.commit()
    db.refresh(db_conference)
    return db_conference

#function to delete conference
def delete_conference(db: Session, conference_id: int):
    db_conference = db.query(models.Conference).filter(models.Conference.id == conference_id).first()
    db.delete(db_conference)
    db.commit()
    return db_conference
