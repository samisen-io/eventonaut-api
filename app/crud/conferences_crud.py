from sqlalchemy.orm import Session
from datetime import datetime, date
from .. import models
from schemas import conference_schemas as schemas
from pytz import timezone

# get all conferences
def get_conferences(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Conference).offset(skip).limit(limit).all()

# create conference
def create_user_conference(db: Session, conference: schemas.ConferenceCreate, user_id: int):
    db_conference = models.Conference(**conference.model_dump(), owner_id=user_id)
    tz = timezone('Asia/Kolkata')
    db_conference.created_on = datetime.now(tz)
    db_conference.updated_on = datetime.now(tz)
    db.add(db_conference)
    db.commit()
    db.refresh(db_conference)
    return db_conference

# get conference by conference id
def get_conference(db: Session, conference_id: int):
    return db.query(models.Conference).filter(models.Conference.id == conference_id).first()

#get conference by owner id and conference id
def get_conference_by_owner_id(db: Session, owner_id: int, conference_id: int):
    return db.query(models.Conference).filter(models.Conference.owner_id == owner_id, models.Conference.id == conference_id).first()

# get conference by name
def get_conferences_by_name(db: Session, name: str):
    return db.query(models.Conference).filter(models.Conference.name == name).all()

# get conference by location
def get_conferences_by_location(db: Session, location: str):
    return db.query(models.Conference).filter(models.Conference.location == location).all()

# get conference by start_date
def get_conferences_by_start_date(db: Session, start_date: date):
    return db.query(models.Conference).filter(models.Conference.start_date == start_date).all()

# get conference by end_date
def get_conferences_by_end_date(db: Session, end_date: str):
    return db.query(models.Conference).filter(models.Conference.end_date == end_date).all()

# get conference by description
def get_conferences_by_description(db: Session, description: str):
    return db.query(models.Conference).filter(models.Conference.description == description).all()

# get conferences by owner_id by name
def get_conferences_owner_id_by_name(db: Session, name: str, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.name == name, models.Conference.owner_id == owner_id).all()

# get conferences by owner_id by location
def get_conferences_owner_id_by_location(db: Session, location: str, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.location == location, models.Conference.owner_id == owner_id).all()

# get conferences by owner_id by start_date
def get_conferences_owner_id_by_start_date(db: Session, start_date: str, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.start_date == start_date, models.Conference.owner_id == owner_id).all()

# get conferences by owner_id by end_date
def get_conferences_owner_id_by_end_date(db: Session, end_date: str, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.end_date == end_date, models.Conference.owner_id == owner_id).all()

# get conferences by owner_id by description
def get_conferences_owner_id_by_description(db: Session, description: str, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.description == description, models.Conference.owner_id == owner_id).all()

# get conferences by owner_id
def get_conferences_by_owner_id(db: Session, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.owner_id == owner_id).all()

# get all conferences by owner_id and conference_id and between start_date and end_date order by start_date
def get_conferences_by_owner_id_between_start_date_and_end_date(db: Session, owner_id: int, filter_start_date: date, filter_end_date: date):
    return db.query(models.Conference).filter(models.Conference.owner_id == owner_id, models.Conference.start_date >= filter_start_date, models.Conference.start_date <= filter_end_date).order_by(models.Conference.start_date).all()

# delete conference by conference id
def delete_conference(db: Session,owner_id: int, conference_id: int):
    db.query(models.Conference).filter(models.Conference.id == conference_id, models.Conference.owner_id==owner_id).delete()
    db.query(models.Session).filter(models.Session.conference_id == conference_id, models.Session.owner_id==owner_id).delete()
    db.query(models.Settings).filter(models.Settings.conference_id == conference_id, models.Settings.owner_id==owner_id).delete()
    db.commit()
    return True

# delete all conferences by owner id
def delete_all_conferences_of_owner_id(db: Session, owner_id: int):
    db.query(models.Conference).filter(models.Conference.owner_id == owner_id).delete()
    db.query(models.Session).filter(models.Session.owner_id == owner_id).delete()
    db.query(models.Settings).filter(models.Settings.owner_id == owner_id).delete()
    db.commit()
    return True

# update conference by conference id
def update_user_conference(db: Session, conference: schemas.ConferenceCreate, conference_id: int):
    db_conference = db.query(models.Conference).filter(models.Conference.id == conference_id).first()
    tz = timezone('Asia/Kolkata')
    db_conference.name = conference.name
    db_conference.location = conference.location
    db_conference.start_date = conference.start_date
    db_conference.end_date = conference.end_date
    db_conference.description = conference.description
    db_conference.updated_on = datetime.now(tz)
    db.commit()
    db.refresh(db_conference)
    return db_conference

# update conference by owner id and conference id
def update_conference(db: Session, conference: schemas.ConferenceCreate, owner_id: int, conference_id: int):
    db_conference = db.query(models.Conference).filter(models.Conference.id == conference_id, models.Conference.owner_id == owner_id).first()
    tz = timezone('Asia/Kolkata')
    db_conference.name = conference.name
    db_conference.location = conference.location
    db_conference.start_date = conference.start_date
    db_conference.end_date = conference.end_date
    db_conference.description = conference.description
    db_conference.updated_on = datetime.now(tz)
    db.commit()
    db.refresh(db_conference)
    return db_conference
