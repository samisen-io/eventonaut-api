import logging
from sqlalchemy.orm import Session
from app import models
import app.schemas.backdrop_gallery_schemas as schemas
import app.crud.conferences_crud as conferences_crud
from datetime import datetime
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import joinedload
from sqlalchemy import text
from ..routers import upload_image
from ..static_enums.blob_container_enums import BlobContainer
from urllib.parse import urlparse, unquote
import re

def get_all_backdrops_by_organization_id(db: Session, organization_id: int, offset: int = 0, limit: int = 100):
    backdrops = db.query(models.BackdropGallery).options(
        joinedload(models.BackdropGallery.conference)
    ).filter(
        models.BackdropGallery.organization_id == organization_id,
        models.BackdropGallery.is_archived == False
    ).offset(offset).limit(limit).all()
    return backdrops

def extract_filename(url: str) -> str:
    parsed_url = urlparse(url)
    filename_with_extension = unquote(parsed_url.path.split('/')[-1])
    filename = filename_with_extension.split('.')[0]

    filename = re.sub(r'dyn-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}-', '', filename)

    return filename

def get_backdrop(db: Session, backdrop_id: str):
    backdrop = db.query(models.BackdropGallery).filter(models.BackdropGallery.uuid == backdrop_id).first()
    if backdrop is None:
        logging.exception(f"Backdrop not found")
        raise HTTPException(status_code=404, detail="Backdrop not found")
    return backdrop

def get_backdrop_by_id(db: Session, backdrop_id: str, organization_id: int):
    backdrop = db.query(models.BackdropGallery).options(
        joinedload(models.BackdropGallery.organization),
        joinedload(models.BackdropGallery.conference)
    ).filter(
        models.BackdropGallery.uuid == backdrop_id,
        models.Organization.id == organization_id,
        models.BackdropGallery.is_archived == False,
        models.Organization.is_archived == False,
    ).first()

    if backdrop is None:
        raise HTTPException(status_code=404, detail="Backdrop not found")
    return backdrop

def execute_backdrop_query(db: Session, conference_id: str, organization_id: int, skip: int = 0, limit: int = 100):
    result = db.execute(
        text("""
        SELECT 
            backdrop_gallery.id as id,
            backdrop_gallery.uuid as uuid,
            backdrop_gallery.backdrop_url as backdrop_url,
            backdrop_gallery.name as name,
            backdrop_gallery.size as size,
            backdrop_gallery.created_on as created_on,
            backdrop_gallery.updated_on as updated_on,
            backdrop_gallery.is_archived as is_archived,
            backdrop_gallery.organization_id as organization_id,
            backdrop_gallery.conference_id as conference_id
        FROM 
            backdrop_gallery
        JOIN 
            organization ON backdrop_gallery.organization_id = organization.id
        JOIN 
            conferences ON backdrop_gallery.conference_id = conferences.id
        WHERE 
            backdrop_gallery.is_archived = false AND 
            conferences.id = :conference_id AND 
            conferences.is_archived = false AND
            backdrop_gallery.organization_id = :organization_id
        OFFSET :skip
        LIMIT :limit
        """),
        {"conference_id": conference_id, "organization_id": organization_id, "skip": skip, "limit": limit}
    ).fetchall()
    return result

def create_backdrop_objects(result):
    backdrops = []
    for row in result:
        backdrop = models.BackdropGallery(
            id=row.id,
            uuid=row.uuid,
            backdrop_url=row.backdrop_url,
            name=row.name,
            size=row.size,
            created_on=row.created_on,
            updated_on=row.updated_on,
            is_archived=row.is_archived,
            organization_id=row.organization_id,
            conference_id=row.conference_id
        )
        backdrops.append(backdrop)
    return backdrops

def check_backdrops(backdrops):
    if not backdrops:
        raise HTTPException(status_code=404, detail="No backdrops found")

def get_backdrops_by_conference_id(db: Session, conference_id: str, organization_id: int, skip: int = 0, limit: int = 100):
    result = execute_backdrop_query(db, conference_id, organization_id, skip, limit)
    backdrops = create_backdrop_objects(result)
    check_backdrops(backdrops)
    return backdrops

def get_backdrops_by_conference(db: Session, conference_id: str, skip: int = 0, limit: int = 100):
    result = db.query(models.BackdropGallery).options(joinedload(models.BackdropGallery.conference)).filter(models.BackdropGallery.conference_id == conference_id,models.BackdropGallery.is_archived == False).offset(skip).limit(limit).all()
    backdrops = create_backdrop_objects(result)
    check_backdrops(backdrops)
    return backdrops

def create_backdrop(db: Session, backdrop: schemas.BackdropGalleryCreate, organization_id: int):
    try:
        conference = conferences_crud.get_conference_by_uuid(db=db, uuid=backdrop.conference_id, organization_id=organization_id)

        backdrops = db.query(models.BackdropGallery).filter(
            models.BackdropGallery.conference_id == conference.id,
            models.BackdropGallery.is_archived == False
        ).count()

        if backdrops >= 3:
            raise HTTPException(status_code=400, detail="A conference can only have three backdrops")
        
        original_filename = extract_filename(backdrop.backdrop_url)
        
        db_backdrop = models.BackdropGallery(organization_id=organization_id, 
                                         conference_id=conference.id,
                                         name=original_filename)
        db_backdrop.created_on = db_backdrop.updated_on = datetime.utcnow()
        db_backdrop.uuid = 'bdg-' + str(uuid.uuid4())
        
        db_backdrop.backdrop_url = upload_image.get_actual_url(image_url=backdrop.backdrop_url, new_blob_container=BlobContainer.BACKDROP_IMAGES.value, new_blob_name=f"back-drop-{db_backdrop.uuid}-{original_filename}") if backdrop.backdrop_url else None
                
        db_backdrop.size = upload_image.get_blob_size_by_url(db_backdrop.backdrop_url)
        
        db.add(db_backdrop)
        try:
            db.commit()
        except Exception as e:
            upload_image.delete_blob_by_url(db_backdrop.backdrop_url)
            logging.exception(str(e))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        db.refresh(db_backdrop)
        return db_backdrop
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))

def update_backdrop(db: Session, backdrop: schemas.BackdropGalleryUpdate, db_backdrop: models.BackdropGallery):
    backdrop_dict = backdrop.model_dump()
    
    backdrop_dict.pop('id', None)
    backdrop_image = backdrop_dict.pop('backdrop_url')
    
    for key, value in backdrop_dict.items():
        setattr(db_backdrop, key, value)
        
    if backdrop_image is not None and upload_image.get_container_name_from_url(backdrop_image) != BlobContainer.BACKDROP_IMAGES.value:
        db_backdrop.backdrop_url = upload_image.get_actual_url(image_url=backdrop_image, new_blob_container=BlobContainer.BACKDROP_IMAGES.value, new_blob_name=f"back-drop-{db_backdrop.uuid}")
    elif backdrop_image is None and db_backdrop.backdrop_url is not None:
        upload_image.delete_blob_by_url(db_backdrop.backdrop_url)
        db_backdrop.backdrop_url = None
    
    db_backdrop.size = upload_image.get_blob_size_by_url(db_backdrop.backdrop_url)
    
    db_backdrop.updated_on = datetime.utcnow()
    try:
        db.commit()
    except Exception as e:
        if backdrop_image is not None:
            upload_image.delete_blob_by_url(db_backdrop.backdrop_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_backdrop)
    return db_backdrop

def delete_backdrop(db: Session, db_backdrop: models.BackdropGallery):
    upload_image.delete_blob_by_url(db_backdrop.backdrop_url)
    db.refresh(db_backdrop)
    db.delete(db_backdrop)
    db.commit()
    return True