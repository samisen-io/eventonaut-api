from sqlalchemy.orm import Session
from datetime import datetime
from .. import models
from ..schemas import settings_schemas as schemas
import uuid

#crud for settings
def get_settings(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.Settings).offset(offset).limit(limit).all()

#get settings by id
def get_settings_by_id(db: Session, settings_id: int):
    return db.query(models.Settings).filter(models.Settings.id == settings_id).first()

#create settings
def create_settings(db: Session, settings: schemas.SettingsCreate, organization_id: int):
    db_settings = models.Settings(body=settings.body)
    db_settings.organization_id = organization_id
    db_settings.created_on = datetime.utcnow()
    db_settings.updated_on = datetime.utcnow()
    db_settings.uuid = "set-" + str(uuid.uuid4())
    conference_id = db.query(models.Conference).filter(models.Conference.uuid == settings.conference_id, models.Conference.organization_id == organization_id).first().id
    db_settings.conference_id = conference_id
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings

def get_settings_by_conference_uuid(db: Session, conference_uuid: str, organization_id: int):
    conference_id = db.query(models.Conference).filter(models.Conference.uuid == conference_uuid, models.Conference.organization_id == organization_id).first().id
    return db.query(models.Settings).filter(models.Settings.conference_id == conference_id, models.Settings.organization_id == organization_id).first()

def get_settings_by_conf_uuid(db: Session, conference_uuid: int):
    conference_id = db.query(models.Conference).filter(models.Conference.uuid == conference_uuid).first().id
    return db.query(models.Settings).filter(models.Settings.conference_id == conference_id).first()

def get_settings_by_body(db: Session, body: str):
    return db.query(models.Settings).filter(models.Settings.body == body).all()

#get settings by body by conference_id
def get_settings_by_body_conference_id(db: Session, body: str, conference_id: int):
    return db.query(models.Settings).filter(models.Settings.body == body, models.Settings.conference_id == conference_id).all()

#update settings
def update_settings(db: Session, settings:schemas.SettingsCreate, organization_id: int):
    conference_id = db.query(models.Conference).filter(models.Conference.uuid == settings.conference_uuid, models.Conference.organization_id == organization_id).first().id
    db_settings = db.query(models.Settings).filter(models.Settings.conference_id == conference_id, models.Settings.organization_id == organization_id).first()
    db_settings.body = settings.body
    db_settings.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_settings)
    return db_settings

#delete settings with conference id and settings id
def delete_settings(db: Session, conference_uuid: int, organization_id: int):
    conference_id = db.query(models.Conference).filter(models.Conference.uuid == conference_uuid, models.Conference.organization_id == organization_id).first().id
    db.query(models.Settings).filter(models.Settings.conference_id == conference_id,models.Settings.organization_id == organization_id).delete()
    db.commit()
    return True