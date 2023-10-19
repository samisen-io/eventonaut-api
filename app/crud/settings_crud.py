from sqlalchemy.orm import Session
from datetime import datetime
from .. import models
import pytz

#crud for settings
def get_settings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Settings).offset(skip).limit(limit).all()

#get settings by id
def get_settings_by_id(db: Session, settings_id: int):
    return db.query(models.Settings).filter(models.Settings.id == settings_id).first()

#create settings
def create_settings(db: Session, body: dict, conference_id: int):
    tz = pytz.timezone('Asia/Kolkata')
    owner_id=db.query(models.Conference).filter(models.Conference.id == conference_id).first().owner_id
    db_settings = models.Settings(body=body, conference_id=conference_id,owner_id=owner_id, created_on=datetime.now(tz), updated_on=datetime.now(tz))
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings

def get_settings_by_conference_id(db: Session, conference_id: int):
    return db.query(models.Settings).filter(models.Settings.conference_id == conference_id).first()

def get_settings_by_body(db: Session, body: str):
    return db.query(models.Settings).filter(models.Settings.body == body).all()

#get settings by body by conference_id
def get_settings_by_body_conference_id(db: Session, body: str, conference_id: int):
    return db.query(models.Settings).filter(models.Settings.body == body, models.Settings.conference_id == conference_id).all()

#delete settings with conference id and settings id
def delete_settings(db: Session, conference_id: int):
    db.query(models.Settings).filter(models.Settings.conference_id == conference_id).delete()
    db.commit()
    return True

#update settings
def update_settings(db: Session, body: str, conference_id: int):
    db_settings = db.query(models.Settings).filter(models.Settings.conference_id == conference_id).first()
    db_settings.body = body
    db_settings.updated_on = datetime.now(pytz.timezone('Asia/Kolkata'))
    db.commit()
    db.refresh(db_settings)
    return db_settings