from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

#get user by email ignore case
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email.ilike(email)).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

#create user
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#update user
def update_user(db: Session, user: schemas.UserCreate, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.email = user.email
    db_user.first_name = user.first_name
    db_user.last_name = user.last_name
    db_user.account_type = user.account_type
    db_user.bussiness_type = user.bussiness_type
    db.commit()
    db.refresh(db_user)
    return db_user

#delete user
def delete_user(db: Session, user_id: int):
    db.query(models.User).filter(models.User.id == user_id).delete()
    db.commit()
    return True

#get user by account_type
def get_users_by_account_type(db: Session, account_type: str):
    return db.query(models.User).filter(models.User.account_type == account_type).all()

#get user by bussiness_type
def get_users_by_bussiness_type(db: Session, bussiness_type: str):
    return db.query(models.User).filter(models.User.bussiness_type == bussiness_type).all()

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

def get_conferences_by_name(db: Session, name: str):
    return db.query(models.Conference).filter(models.Conference.name == name).all()

def get_conferences_by_location(db: Session, location: str):
    return db.query(models.Conference).filter(models.Conference.location == location).all()

def get_conferences_by_start_date(db: Session, start_date: str):
    return db.query(models.Conference).filter(models.Conference.start_date == start_date).all()

def get_conferences_by_end_date(db: Session, end_date: str):
    return db.query(models.Conference).filter(models.Conference.end_date == end_date).all()

def get_conferences_by_description(db: Session, description: str):
    return db.query(models.Conference).filter(models.Conference.description == description).all()

#get conferences by name by owner_id
def get_conferences_by_name_owner_id(db: Session, name: str, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.name == name, models.Conference.owner_id == owner_id).all()

#get conferences by location by owner_id
def get_conferences_by_location_owner_id(db: Session, location: str, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.location == location, models.Conference.owner_id == owner_id).all()

#get conferences by start_date by owner_id
def get_conferences_by_start_date_owner_id(db: Session, start_date: str, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.start_date == start_date, models.Conference.owner_id == owner_id).all()

#get conferences by end_date by owner_id
def get_conferences_by_end_date_owner_id(db: Session, end_date: str, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.end_date == end_date, models.Conference.owner_id == owner_id).all()

#get conferences by description by owner_id
def get_conferences_by_description_owner_id(db: Session, description: str, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.description == description, models.Conference.owner_id == owner_id).all()

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

#crud for session
def get_sessions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Session).offset(skip).limit(limit).all()

def create_conference_session(db: Session, session: schemas.SessionCreate, conference_id: int):
    db_session = models.Session(**session.model_dump(), conference_id=conference_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_session(db: Session, session_id: int):
    return db.query(models.Session).filter(models.Session.id == session_id).first()

def get_sessions_by_name(db: Session, name: str):
    return db.query(models.Session).filter(models.Session.name == name).all()

def get_sessions_by_date(db: Session, date: str):
    return db.query(models.Session).filter(models.Session.date == date).all()

def get_sessions_by_start_time(db: Session, start_time: str):
    return db.query(models.Session).filter(models.Session.start_time == start_time).all()

def get_sessions_by_end_time(db: Session, end_time: str):
    return db.query(models.Session).filter(models.Session.end_time == end_time).all()

def get_sessions_by_location(db: Session, location: str):
    return db.query(models.Session).filter(models.Session.location == location).all()

def get_sessions_by_description(db: Session, description: str):
    return db.query(models.Session).filter(models.Session.description == description).all()

#get sessions from date by conference_id
def get_sessions_by_date_conference_id(db: Session, date: str, conference_id: int):
    return db.query(models.Session).filter(models.Session.date == date, models.Session.conference_id == conference_id).all()

#get sessions by start_time by conference_id
def get_sessions_by_start_time_conference_id(db: Session, start_time: str, conference_id: int):
    return db.query(models.Session).filter(models.Session.start_time == start_time, models.Session.conference_id == conference_id).all()

#get sessions by end_time by conference_id
def get_sessions_by_end_time_conference_id(db: Session, end_time: str, conference_id: int):
    return db.query(models.Session).filter(models.Session.end_time == end_time, models.Session.conference_id == conference_id).all()

#get sessions by location by conference_id
def get_sessions_by_location_conference_id(db: Session, location: str, conference_id: int):
    return db.query(models.Session).filter(models.Session.location == location, models.Session.conference_id == conference_id).all()

#get sessions by description by conference_id
def get_sessions_by_description_conference_id(db: Session, description: str, conference_id: int):
    return db.query(models.Session).filter(models.Session.description == description, models.Session.conference_id == conference_id).all()

#get sessions by conference_id
def get_sessions_by_conference_id(db: Session, conference_id: int):
    return db.query(models.Session).filter(models.Session.conference_id == conference_id).all()

#delete session
def delete_session(db: Session, session_id: int):
    db.query(models.Session).filter(models.Session.id == session_id).delete()
    db.commit()
    return True

#update session
def update_session(db: Session, session: schemas.SessionCreate, session_id: int):
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    db_session.name = session.name
    db_session.date = session.date
    db_session.start_time = session.start_time
    db_session.end_time = session.end_time
    db_session.location = session.location
    db_session.description = session.description
    db.commit()
    db.refresh(db_session)
    return db_session