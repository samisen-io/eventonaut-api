from .. models import Exhibitor, EventExhibitor
from ..schemas import exhibitor_schemas as schemas
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from ..routers import upload_image
from ..static_enums.blob_container_enums import BlobContainer
import logging
from fastapi import HTTPException, status

def get_exhibitors_by_organization_id(db: Session, organization_id: int):
    return db.query(Exhibitor).filter(Exhibitor.organization_id == organization_id, Exhibitor.is_archived == False).all()

def get_exhibitors(db: Session, conference_id: int):
    return db.query(Exhibitor).join(EventExhibitor, EventExhibitor.exhibitor_id == Exhibitor.id).filter(EventExhibitor.conference_id == conference_id, Exhibitor.is_archived == False).all()

def get_exhibitor(db: Session, exhibitor_id: str):
    return db.query(Exhibitor).filter(Exhibitor.uuid == exhibitor_id, Exhibitor.is_archived == False).first()

def get_exhibitor_by_id(db: Session, exhibitor_id: str, organization_id: int):
    return db.query(Exhibitor).filter(Exhibitor.uuid == exhibitor_id, Exhibitor.organization_id == organization_id, Exhibitor.is_archived == False).first()

def create_exhibitor(db: Session, exhibitor: schemas.ExhibitorCreate, organization_id: int):
    exhibitor_dict = exhibitor.model_dump()
    exhibitor_logo = exhibitor_dict.pop('exhibitor_logo', None)
    exhibitor_banner = exhibitor_dict.pop('exhibitor_banner', None)
    exhibitor_dict.pop('conference_id', None)
    db_exhibitor = Exhibitor(**exhibitor_dict)
    db_exhibitor.created_on = db_exhibitor.updated_on = datetime.utcnow()
    db_exhibitor.uuid = 'exb-' + str(uuid.uuid4())
    db_exhibitor.organization_id = organization_id
        
    db_exhibitor.exhibitor_logo = upload_image.get_actual_url(image_url=exhibitor_logo, new_blob_container=BlobContainer.EXHIBITOR_LOGOS.value, new_blob_name=f"exb-logo-{db_exhibitor.uuid}") if exhibitor_logo else None
    
    db_exhibitor.exhibitor_banner = upload_image.get_actual_url(image_url=exhibitor_banner, new_blob_container=BlobContainer.EXHIBITOR_BANNERS.value, new_blob_name=f"exb-banner-{db_exhibitor.uuid}") if exhibitor_banner else None
    
    db.add(db_exhibitor)
    try:
        db.commit()
    except Exception as e:
        upload_image.delete_blob_by_url(db_exhibitor.exhibitor_logo)
        upload_image.delete_blob_by_url(db_exhibitor.exhibitor_banner)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_exhibitor)
    return db_exhibitor

def update_exhibitor(db: Session, db_exhibitor: Exhibitor, exhibitor: schemas.ExhibitorUpdate):
    exhibitor_dict = exhibitor.model_dump()
    exhibitor_dict.pop('id', None)
    exhibitor_logo = exhibitor_dict.pop('exhibitor_logo', None)
    exhibitor_banner = exhibitor_dict.pop('exhibitor_banner', None)
    
    for key, value in exhibitor_dict.items():
        if value is not None:
            setattr(db_exhibitor, key, value)
            
    if exhibitor_logo is not None and upload_image.get_container_name_from_url(exhibitor_logo) != BlobContainer.EXHIBITOR_LOGOS.value:
        db_exhibitor.exhibitor_logo = upload_image.get_actual_url(image_url=exhibitor_logo, new_blob_container=BlobContainer.EXHIBITOR_LOGOS.value, new_blob_name=f"event-logo-{db_exhibitor.uuid}")
    elif exhibitor_logo is None and db_exhibitor.exhibitor_logo is not None:
        upload_image.delete_blob_by_url(db_exhibitor.exhibitor_logo)
        db_exhibitor.exhibitor_logo = None
        
    if exhibitor_banner is not None and upload_image.get_container_name_from_url(exhibitor_banner) != BlobContainer.EXHIBITOR_BANNERS.value:
        db_exhibitor.exhibitor_banner = upload_image.get_actual_url(image_url=exhibitor_banner, new_blob_container=BlobContainer.EXHIBITOR_BANNERS.value, new_blob_name=f"event-banner-{db_exhibitor.uuid}")
    elif exhibitor_banner is None and db_exhibitor.exhibitor_banner is not None:
        upload_image.delete_blob_by_url(db_exhibitor.exhibitor_banner)
        db_exhibitor.exhibitor_banner = None
        
    db_exhibitor.updated_on = datetime.utcnow()
    
    try:
        db.commit()
    except Exception as e:
        if exhibitor_logo is not None:
            upload_image.delete_blob_by_url(db_exhibitor.exhibitor_logo)    
        if exhibitor_banner is not None:
            upload_image.delete_blob_by_url(db_exhibitor.exhibitor_banner)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_exhibitor)
    return db_exhibitor

def delete_exhibitor(db: Session, db_exhibitor: Exhibitor):
    db_exhibitor.is_archived = True
    try:
        db.commit()
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return True