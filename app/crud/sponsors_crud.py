import logging
from fastapi import HTTPException, status
from app.routers import upload_image
from ..import models
from ..schemas import sponsor_schemas
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from ..static_enums.blob_container_enums import BlobContainer
from sqlalchemy.orm import joinedload, Load, defaultload, join, aliased

def get_sponsors_by_organization_id(db: Session, organization_id: int, offset: int = 0, limit: int = 100):
    return db.query(models.Sponsors).filter(
        models.Sponsors.organization_id == organization_id, 
        models.Sponsors.is_archived == False).order_by(
            models.Sponsors.updated_on.desc()).offset(offset).limit(limit).all()

def get_all_sponsors(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.Sponsors).order_by(models.Sponsors.updated_on.desc()).offset(offset).limit(limit).all()

def get_all_sponsors_by_organization_id(db: Session, organization_id: int, offset: int = 0, limit: int = 100):
    return db.query(models.Sponsors).filter(models.Sponsors.organization_id == organization_id, models.Sponsors.is_archived == False).order_by(models.Sponsors.updated_on.desc()).offset(offset).limit(limit).all()

def get_sponsor_by_uuid(db: Session, uuid: str, organization_id: int):
    sponsor = db.query(models.Sponsors).filter(models.Sponsors.uuid == uuid, models.Sponsors.organization_id == organization_id, models.Sponsors.is_archived == False).first()
    return sponsor

def get_sponsor_by_email(db: Session, email: str, organization_id: int):
    return db.query(models.Sponsors).filter(models.Sponsors.email == email, models.Sponsors.organization_id == organization_id, models.Sponsors.is_archived == False).first()

def get_sponsors_by_conference_id(db: Session, conference_id: int, offset: int = 0, limit: int = 100):
    SponsorsAlias = aliased(models.Sponsors)
    sponsors_subquery = db.query(SponsorsAlias).filter(SponsorsAlias.is_archived == False).subquery()
    return db.query(models.EventSponsors).join(sponsors_subquery, models.EventSponsors.sponsor_id == sponsors_subquery.c.id).filter(models.EventSponsors.conference_id == conference_id).order_by(models.EventSponsors.updated_on.desc()).offset(offset).limit(limit).all()

def create_sponsor(db: Session, sponsor: sponsor_schemas.SponsorCreate, organization_id: int):
    sponsor_dict = sponsor.model_dump()
    db_sponsor = models.Sponsors(**sponsor_dict, organization_id=organization_id)
    db_sponsor.created_on = db_sponsor.updated_on = datetime.now()
    db_sponsor.uuid = 'spn-' + str(uuid.uuid4())
    
    if db_sponsor.logo_image_url is not None:
        try:
            db_sponsor.logo_image_url = upload_image.get_actual_url(image_url=sponsor.logo_image_url, new_blob_container=BlobContainer.SPONSOR_LOGOS.value, new_blob_name=f"sponsor-{db_sponsor.uuid}")
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
    sponsor_image_url = sponsor_dict.pop('logo_image_url')
    
    non_nullable_fields = ['email', 'name', 'contact_name', 'contact_phone', 'sponsorship_level']
    
    for key, value in sponsor_dict.items():
        if key in non_nullable_fields:
            if value is not None:
                setattr(db_sponsor, key, value)
        else:
            setattr(db_sponsor, key, value)
    
    db_sponsor.updated_on = datetime.now()
    
    if sponsor_image_url is not None and upload_image.get_container_name_from_url(sponsor_image_url) != BlobContainer.SPONSOR_LOGOS.value:
        db_sponsor.logo_image_url = upload_image.get_actual_url(image_url=sponsor_image_url, new_blob_container=BlobContainer.SPONSOR_LOGOS.value, new_blob_name=f"sponsor-{db_sponsor.uuid}")
    elif sponsor_image_url is None and db_sponsor.logo_image_url is not None:
        upload_image.delete_blob_by_url(db_sponsor.logo_image_url)
        db_sponsor.logo_image_url = None
    
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
    
    if db_sponsor.conference and any([conference.is_archived == False for conference in db_sponsor.conference]):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Sponsor is associated with a conference. Cannot delete sponsor.")
    
    db_sponsor.is_archived = True
    db.commit()
    return True