from ..import models
from ..schemas import sponsor_schemas
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

def get_all_sponsors(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.Sponsors).offset(offset).limit(limit).all()

def get_sponsor_by_uuid(db: Session, uuid: str):
    return db.query(models.Sponsors).filter(models.Sponsors.uuid == uuid).first()

def get_sponsor_by_email(db: Session, email: str):
    return db.query(models.Sponsors).filter(models.Sponsors.email == email).first()

def get_sponsors_by_conference_id(db: Session, conference_id: int, offset: int = 0, limit: int = 100):
    return db.query(models.Sponsors).filter(models.Sponsors.conference_id == conference_id).offset(offset).limit(limit).all()

def create_sponsor(db: Session, sponsor: sponsor_schemas.SponsorCreate, conference_id: int):
    sponsor_dict = sponsor.model_dump()
    sponsor_dict.pop('conference_id')
    db_sponsor = models.Sponsors(**sponsor_dict, conference_id=conference_id)
    db_sponsor.created_on = db_sponsor.updated_on = datetime.now()
    db_sponsor.uuid = 'spn-' + str(uuid.uuid4())
    db.add(db_sponsor)
    db.commit()
    db.refresh(db_sponsor)
    return db_sponsor

def update_sponsor(db: Session, sponsor: sponsor_schemas.SponsorUpdate):
    db_sponsor = db.query(models.Sponsors).filter(models.Sponsors.uuid == sponsor.id).first()
    sponsor_dict = sponsor.model_dump()
    sponsor_dict.pop('id')
    sponsor_dict.pop('conference_id')
    for key, value in sponsor_dict.items():
        if value is not None:
            setattr(db_sponsor, key, value)
    if sponsor.conference_id is not None:
        db_sponsor.conference_id = db.query(models.Conference).filter(models.Conference.uuid == sponsor.conference_id).first().id
    db_sponsor.updated_on = datetime.now()
    db.commit()
    db.refresh(db_sponsor)
    return db_sponsor

def delete_sponsor(db: Session, uuid: str):
    db_sponsor = db.query(models.Sponsors).filter(models.Sponsors.uuid == uuid).first()
    db.delete(db_sponsor)
    db.commit()
    return True