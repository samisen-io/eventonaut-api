from sqlalchemy.orm import Session
from app import models
import schemas.backdrop_gallery_schemas as schemas
from app.crud import users_crud
import conferences_crud as conferences_crud
from datetime import datetime
import uuid
from fastapi import HTTPException

def get_backdrop_by_id(db: Session, backdrop_id: str, owner_id: str):
    backdrop = db.query(models.BackdropGallery).filter(
        models.BackdropGallery.uuid == backdrop_id, 
        models.BackdropGallery.User.uuid == owner_id, 
        models.BackdropGallery.is_archived == False, 
        models.BackdropGallery.User.is_archived == False, 
        models.BackdropGallery.Conference.is_archived == False
    ).first()

    if backdrop is None:
        raise HTTPException(status_code=404, detail="Backdrop not found")

    return backdrop

def get_backdrops_by_conference_id(db: Session, conference_id: str, owner_id: str, skip: int = 0, limit: int = 100):
    backdrops = db.query(models.BackdropGallery).filter(
        models.BackdropGallery.Conference.uuid == conference_id, 
        models.BackdropGallery.User.uuid == owner_id, 
        models.BackdropGallery.is_archived == False, 
        models.BackdropGallery.User.is_archived == False, 
        models.BackdropGallery.Conference.is_archived == False
    ).offset(skip).limit(limit).all()

    if not backdrops:
        raise HTTPException(status_code=404, detail="No backdrops found")

    return backdrops

def create_backdrop(db: Session, backdrop: schemas.BackdropGalleryCreate, owner_id: str):
    user = users_crud.get_user_by_uuid(db, owner_id)
    conference = conferences_crud.get_conference_by_uuid(backdrop.conference_id)
    
    db_backdrop = models.BackdropGallery(**backdrop.model_dump(), owner_id=user.id, conference_id=conference.id)
    db_backdrop.created_on = db_backdrop.updated_on = datetime.utcnow()
    db_backdrop.uuid = 'bdg-' + str(uuid.uuid4())
    db.add(db_backdrop)
    db.commit()
    db.refresh(db_backdrop)
    return db_backdrop

def update_backdrop(db: Session, backdrop: schemas.BackdropGalleryCreate, db_backdrop: models.BackdropGallery):
    backdrop_dict = backdrop.model_dump()
    for key, value in backdrop_dict.items():
        setattr(db_backdrop, key, value)
    db_backdrop.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_backdrop)
    return db_backdrop

def delete_backdrop(db: Session, db_backdrop: models.BackdropGallery):
    db.delete(db_backdrop)
    db.commit()
    return True