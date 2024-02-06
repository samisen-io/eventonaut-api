from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..schemas import venue_schemas
from .. import models
import uuid
from datetime import datetime

def get_all_venues(db: Session, offset: int, limit: int):
    return db.query(models.Venue).offset(offset).limit(limit).all()

def get_all_venues_by_owner_id(db: Session, owner_id: int, offset: int, limit: int):
    return db.query(models.Venue).filter(models.Venue.owner_id == owner_id, models.Venue.is_archived == False).offset(offset).limit(limit).all()

def get_venue_by_id(db: Session, venue_id: str, owner_id: int):
    return db.query(models.Venue).filter(models.Venue.uuid == venue_id, models.Venue.owner_id == owner_id, models.Venue.is_archived == False).first()

def create_venue(db: Session, venue: venue_schemas.VenueCreate, owner_id: int):
    db_venue = models.Venue(**venue.model_dump(), owner_id=owner_id)
    db_venue.created_on = db_venue.updated_on = datetime.utcnow()
    db_venue.uuid = 'ven-' + str(uuid.uuid4())
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)
    return db_venue

def update_venue(db: Session, venue: venue_schemas.VenueUpdate, db_venue: models.Venue):
    venue_dict = venue.model_dump()
    db_venue.geo_location = venue_dict.pop('geo_location')
    venue_dict.pop('id')

    for key, value in venue_dict.items():
        if value is not None:
            setattr(db_venue, key, value)

    db_venue.updated_on = datetime.utcnow()

    db.commit()
    db.refresh(db_venue)
    return db_venue

def delete_venue(db: Session, db_venue: models.Venue):
    db_venue.is_archived = True
    db.commit()
    return True