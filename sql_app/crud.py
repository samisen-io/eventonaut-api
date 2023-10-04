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


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

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

#delete conference
def delete_conference(db: Session, conference_id: int):
    db.query(models.Conference).filter(models.Conference.id == conference_id).delete()
    db.commit()
    return True

#update conference
def update_conference(db: Session, conference_id: int, conference: schemas.ConferenceCreate):
    db.query(models.Conference).filter(models.Conference.id == conference_id).update(conference.model_dump())
    db.commit()
    return True

