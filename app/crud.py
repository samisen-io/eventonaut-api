from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#crud for conference
def get_conferences(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Conference).offset(skip).limit(limit).all()

def create_user_conference(db: Session, conference: schemas.ConferenceCreate, user_id: int):
    db_conference = models.Conference(**conference.model_dump(), owner_id=user_id)
    db.add(db_conference)
    db.commit()
    db.refresh(db_conference)
    return db_conference

def get_conference(db: Session, conference_id: int):
    return db.query(models.Conference).filter(models.Conference.id == conference_id).first()

def get_conference_by_name(db: Session, name: str):
    return db.query(models.Conference).filter(models.Conference.name == name).first()

def get_conference_by_location(db: Session, location: str):
    return db.query(models.Conference).filter(models.Conference.location == location).first()

def get_conference_by_start_date(db: Session, start_date: str):
    return db.query(models.Conference).filter(models.Conference.start_date == start_date).first()

def get_conference_by_end_date(db: Session, end_date: str):
    return db.query(models.Conference).filter(models.Conference.end_date == end_date).first()

def get_conference_by_description(db: Session, description: str):
    return db.query(models.Conference).filter(models.Conference.description == description).first()

#get conferences by owner_id
def get_conferences_by_owner_id(db: Session, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.owner_id == owner_id).all()

#delete conference
def delete_conference(db: Session, conference_id: int):
    db.query(models.Conference).filter(models.Conference.id == conference_id).delete()
    db.commit()
    return True

#update conference
def update_conference(db: Session, conference: schemas.ConferenceCreate, conference_id: int):
    db_conference = db.query(models.Conference).filter(models.Conference.id == conference_id).first()
    db_conference.name = conference.name
    db_conference.location = conference.location
    db_conference.start_date = conference.start_date
    db_conference.end_date = conference.end_date
    db_conference.description = conference.description
    db.commit()
    db.refresh(db_conference)
    return db_conference
