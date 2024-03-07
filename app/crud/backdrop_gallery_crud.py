import logging
from sqlalchemy.orm import Session
from app import models
import app.schemas.backdrop_gallery_schemas as schemas
import app.crud.conferences_crud as conferences_crud
from datetime import datetime
import uuid
from fastapi import HTTPException
from sqlalchemy.orm import joinedload
from sqlalchemy import text

def get_backdrop_by_id(db: Session, backdrop_id: str, owner_id: str):
    backdrop = db.query(models.BackdropGallery).options(
        joinedload(models.BackdropGallery.User),
        joinedload(models.BackdropGallery.conference)
    ).filter(
        models.BackdropGallery.uuid == backdrop_id
    ).first()

    if backdrop is None:
        raise HTTPException(status_code=404, detail="Backdrop not found")
    
    if backdrop.User.id != owner_id:
        raise HTTPException(status_code=403, detail="Permission denied")
    if backdrop.is_archived or backdrop.User.is_archived or backdrop.conference.is_archived:
        raise HTTPException(status_code=404, detail="Backdrop not found")

    return backdrop

def execute_backdrop_query(db: Session, conference_id: str, owner_id: str, skip: int = 0, limit: int = 100):
    result = db.execute(
        text("""
        SELECT 
            backdrop_gallery.id as id,
            backdrop_gallery.uuid as uuid,
            backdrop_gallery.backdrop_url as backdrop_url,
            backdrop_gallery.created_on as created_on,
            backdrop_gallery.updated_on as updated_on,
            backdrop_gallery.is_archived as is_archived,
            backdrop_gallery.owner_id as owner_id,
            backdrop_gallery.conference_id as conference_id
        FROM 
            backdrop_gallery
        JOIN 
            users ON backdrop_gallery.owner_id = users.id
        JOIN 
            conferences ON backdrop_gallery.conference_id = conferences.id
        WHERE 
            backdrop_gallery.is_archived = false AND 
            conferences.uuid = :conference_id AND 
            backdrop_gallery.owner_id = :owner_id AND 
            conferences.is_archived = false AND 
            users.is_archived = false
        OFFSET :skip
        LIMIT :limit
        """),
        {"conference_id": conference_id, "owner_id": owner_id, "skip": skip, "limit": limit}
    ).fetchall()
    return result

def create_backdrop_objects(result):
    backdrops = []
    for row in result:
        backdrop = models.BackdropGallery(
            id=row.id,
            uuid=row.uuid,
            backdrop_url=row.backdrop_url,
            created_on=row.created_on,
            updated_on=row.updated_on,
            is_archived=row.is_archived,
            owner_id=row.owner_id,
            conference_id=row.conference_id
        )
        backdrops.append(backdrop)
    return backdrops

def check_backdrops(backdrops):
    if not backdrops:
        raise HTTPException(status_code=404, detail="No backdrops found")

def get_backdrops_by_conference_id(db: Session, conference_id: str, owner_id: str, skip: int = 0, limit: int = 100):
    result = execute_backdrop_query(db, conference_id, owner_id, skip, limit)
    backdrops = create_backdrop_objects(result)
    check_backdrops(backdrops)
    return backdrops

def create_backdrop(db: Session, backdrop: schemas.BackdropGalleryCreate, owner_id: int):
    try:
        conference = conferences_crud.get_conference_by_uuid(db=db, uuid=backdrop.conference_id, owner_id=owner_id)

        backdrops = db.query(models.BackdropGallery).filter(
            models.BackdropGallery.conference_id == conference.id,
            models.BackdropGallery.is_archived == False
        ).count()

        if backdrops >= 3:
            raise HTTPException(status_code=400, detail="A conference can only have three backdrops")
        
        db_backdrop = models.BackdropGallery(backdrop_url = backdrop.backdrop_url, 
                                         owner_id=owner_id, 
                                         conference_id=conference.id)
        db_backdrop.created_on = db_backdrop.updated_on = datetime.utcnow()
        db_backdrop.uuid = 'bdg-' + str(uuid.uuid4())
        db.add(db_backdrop)
        db.commit()
        db.refresh(db_backdrop)
        return db_backdrop
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))

def update_backdrop(db: Session, backdrop: schemas.BackdropGalleryUpdate, db_backdrop: models.BackdropGallery):
    backdrop_dict = backdrop.model_dump()
    for key, value in backdrop_dict.items():
        setattr(db_backdrop, key, value)
    db_backdrop.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_backdrop)
    return db_backdrop

def delete_backdrop(db: Session, db_backdrop: models.BackdropGallery):
    db_backdrop.is_archived = True
    db_backdrop.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_backdrop)
    return True