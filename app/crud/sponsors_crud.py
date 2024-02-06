import logging
import os
from urllib.parse import urlparse

from fastapi import HTTPException, status

from app.routers import upload_image
from ..import models
from ..schemas import sponsor_schemas
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

def get_all_sponsors(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.Sponsors).offset(offset).limit(limit).all()

def get_all_sponsors_by_owner_id(db: Session, owner_id: int, offset: int = 0, limit: int = 100):
    return db.query(models.Sponsors).filter(models.Sponsors.owner_id == owner_id, models.Sponsors.isarchived == False).offset(offset).limit(limit).all()

def get_sponsor_by_uuid(db: Session, uuid: str, owner_id: int):
    return db.query(models.Sponsors).filter(models.Sponsors.uuid == uuid, models.Sponsors.owner_id == owner_id, models.Sponsors.isarchived == False).first()

def get_sponsor_by_email(db: Session, email: str, owner_id: int):
    return db.query(models.Sponsors).filter(models.Sponsors.email == email, models.Sponsors.owner_id == owner_id, models.Sponsors.isarchived == False).first()

def get_sponsors_by_conference_id(db: Session, conference_id: int, offset: int = 0, limit: int = 100):
    event_sponsors =  db.query(models.EventSponsors).filter(models.EventSponsors.conference_id == conference_id, models.EventSponsors.isarchived == False).offset(offset).limit(limit).all()
    if not event_sponsors:
        return None
    sponsors = []
    for event_sponsor in event_sponsors:
        if event_sponsor not in sponsors:
            sponsors.append(db.query(models.Sponsors).filter(models.Sponsors.id == event_sponsor.sponsor_id).first())
    return sponsors

def create_sponsor(db: Session, sponsor: sponsor_schemas.SponsorCreate, owner_id: int):
    sponsor_dict = sponsor.model_dump()
    db_sponsor = models.Sponsors(**sponsor_dict, owner_id=owner_id)
    db_sponsor.created_on = db_sponsor.updated_on = datetime.now()
    db_sponsor.uuid = 'spn-' + str(uuid.uuid4())
    
    try:
        db_sponsor.logo_image_url = upload_image.get_actual_url(image_url=sponsor.logo_image_url, new_blob_container="sponsor-logos", new_blob_name=f"sponsor-{db_sponsor.uuid}") 
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    db.add(db_sponsor)
    try:
        db.commit()
    except Exception as e:
        upload_image.delete_blob_by_url(db_sponsor.logo_image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_sponsor)
    return db_sponsor

def update_sponsor(db: Session, sponsor: sponsor_schemas.SponsorUpdate, db_sponsor: models.Sponsors):
    sponsor_dict = sponsor.model_dump()
    sponsor_dict.pop('id')
    sponsor_image_url = sponsor_dict.pop('profile_image_url')
    for key, value in sponsor_dict.items():
        if value is not None:
            setattr(db_sponsor, key, value)
    db_sponsor.updated_on = datetime.now()
    
    if sponsor_image_url is not None:
        db_sponsor.logo_image_url = upload_image.get_actual_url(image_url=sponsor_image_url, new_blob_container="sponsor-logos", new_blob_name=f"sponsor-{db_sponsor.uuid}")
    
    try:
        db.commit()
    except Exception as e:
        if sponsor_image_url is not None:
            upload_image.delete_blob_by_url(db_sponsor.logo_image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_sponsor)
    return db_sponsor

def delete_sponsor(db: Session, db_sponsor: models.Sponsors):
    db_sponsor.isarchived = True
    db.commit()
    return True