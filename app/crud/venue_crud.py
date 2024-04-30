from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..schemas import venue_schemas
from .. import models
import uuid
from datetime import datetime
from fastapi import HTTPException, status

def get_all_venues(db: Session, offset: int, limit: int):
    return db.query(models.Venue).order_by(models.Venue.updated_on.desc()).offset(offset).limit(limit).all()

# def get_all_venues_by_owner_id(db: Session, owner_id: int, offset: int, limit: int):
#     return db.query(models.Venue).filter(models.Venue.owner_id == owner_id, models.Venue.is_archived == False).order_by(models.Venue.updated_on.desc()).offset(offset).limit(limit).all()

def get_all_venues_by_organization_id(db: Session, organization_id: int, offset: int, limit: int):
    return db.query(models.Venue).filter(models.Venue.organization_id == organization_id, models.Venue.is_archived == False).order_by(models.Venue.updated_on.desc()).offset(offset).limit(limit).all()

def get_venue_by_id(db: Session, venue_id: str, owner_id: int):
    return db.query(models.Venue).filter(models.Venue.uuid == venue_id, models.Venue.owner_id == owner_id, models.Venue.is_archived == False).first()

def get_venue_by_id_for_organization(db: Session, venue_id: str, organization_id: int):
    return db.query(models.Venue).filter(models.Venue.uuid == venue_id, models.Venue.organization_id == organization_id, models.Venue.is_archived == False).first()

def create_venue(db: Session, venue: venue_schemas.VenueCreate, owner_id: int):
    db_venue = models.Venue(**venue.model_dump(), owner_id=owner_id)
    db_venue.created_on = db_venue.updated_on = datetime.utcnow()
    db_venue.uuid = 'ven-' + str(uuid.uuid4())
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)
    return db_venue

def create_venue_using_organization_id(db: Session, venue: venue_schemas.VenueCreate, organization_id: int):
    db_venue = models.Venue(**venue.model_dump(), organization_id=organization_id)
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
    
    non_nullable_fields = ['name', 'location']
    
    for key, value in venue_dict.items():
        if key in non_nullable_fields and value is not None:
            setattr(db_venue, key, value)
        elif key not in non_nullable_fields:
            setattr(db_venue, key, value)

    db_venue.updated_on = datetime.utcnow()

    db.commit()
    db.refresh(db_venue)
    return db_venue

def update_venue_by_id(db: Session, venue: venue_schemas.VenueUpdate):
    venue_dict = venue.model_dump()
    db_venue = db.query(models.Venue).filter(models.Venue.uuid == venue_dict['id']).first()
    db_venue.geo_location = venue_dict.pop('geo_location')
    venue_dict.pop('id')
    
    non_nullable_fields = ['name', 'location']
    
    for key, value in venue_dict.items():
        if key in non_nullable_fields and value is not None:
            setattr(db_venue, key, value)
        elif key not in non_nullable_fields:
            setattr(db_venue, key, value)

    db_venue.updated_on = datetime.utcnow()

    db.commit()
    db.refresh(db_venue)
    return db_venue

def delete_venue(db: Session, db_venue: models.Venue):
    if db_venue.conference and any([conference.is_archived == False for conference in db_venue.conference]):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Venue is associated with a conference. Cannot delete venue.")
    
    db_venue.is_archived = True
    db.commit()
    return True