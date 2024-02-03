import logging
import os
from urllib.parse import urlparse

from app.routers import upload_image
from .. import models
from ..schemas import promotion_schemas
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from fastapi import HTTPException, status

def get_promotion(db: Session, promotion_id: str):
    promotion = db.query(models.Promotions).filter(models.Promotions.uuid == promotion_id).first()
    if promotion is not None:
        promotion.location = db.query(models.Conference).filter(models.Conference.id == promotion.conference_id).first().location
        promotion = add_conference_to_promotion(db, promotion)
    return promotion

def get_promotion_by_conference(db: Session, conference_id: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id).first()
    return None if conference is None else db.query(models.Promotions).filter(models.Promotions.conference_id == conference.id).first()

def get_promotions(db: Session, skip: int = 0, limit: int = 100):
    promotions = db.query(models.Promotions).order_by(models.Promotions.rank).offset(skip).limit(limit).all()
    for promotion in promotions:
        promotion.location = db.query(models.Conference).filter(models.Conference.id == promotion.conference_id).first().location
    promotions = add_conference_to_promotion(db, promotions)
    return promotions

def get_all_promotions(db: Session, skip: int = 0, limit: int = 100):
    promotions = db.query(models.Promotions).order_by(models.Promotions.rank).offset(skip).limit(limit).all()
    for promotion in promotions:
        promotion.location = db.query(models.Conference).filter(models.Conference.id == promotion.conference_id).first().location
    promotions = add_conference_to_promotion(db, promotions)
    return promotions

def create_promotion(db: Session, promotion: promotion_schemas.PromotionCreate):
    db_promotion = models.Promotions(**promotion.model_dump())
    db_promotion.uuid = "pro-" + str(uuid.uuid4())
    db_promotion.created_on = db_promotion.updated_on = datetime.utcnow()
    conference = db.query(models.Conference).filter(models.Conference.uuid == promotion.conference_id).first()
    db_promotion.conference_id = conference.id
    
    parsed_url = parsed_url = urlparse(promotion.image_url)
    path = parsed_url.path
    filename_with_ext = os.path.basename(path)
    _, extension = os.path.splitext(filename_with_ext)

    if extension not in ['.jpg', '.jpeg', '.png']:
        logging.exception("Invalid image file format")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file format")
    
    image_url = upload_image.move_file_from_temporary_to_permanent_container(source_container_name="temporary-images", dest_container_name="promotion-images", old_blob_name=filename_with_ext, new_blob_name=f"promotion-{db_promotion.uuid}" + extension)
    
    db_promotion.image_url = image_url
    db.add(db_promotion)
    try:
        db.commit()
    except Exception as e:
        upload_image.delete_blob("promotion-images", f"promotion-{db_promotion.uuid}" + extension)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_promotion)
    promotion = add_conference_to_promotion(db, db_promotion)
    promotion.location = conference.location
    return promotion

def update_promotion(db: Session, promotion: promotion_schemas.PromotionUpdate):
    db_promotion = db.query(models.Promotions).filter(models.Promotions.uuid == promotion.id).first()
    db.refresh(db_promotion)
    promotion: dict = promotion.model_dump()
    promotion_rank = promotion.pop('rank')
    conference_id = promotion.pop('conference_id')
    promotion_image_url = promotion.pop('image_url')
    promotion.pop('id')
    updates = promotion
    for key, value in updates.items():
        if value is not None:
            setattr(db_promotion, key, value)
   
    if db_promotion.fromdate > db_promotion.todate:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date range")

    if promotion_rank != 0:
        db_promotion.rank = promotion_rank

    if conference_id is not None:
        db_conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id).first()
        db_promotion.conference_id = db_conference.id
        promotion.location = db_conference.location

    if promotion_image_url is not None:
        parsed_url = urlparse(promotion_image_url)
        path = parsed_url.path
        filename_with_ext = os.path.basename(path)
        _, extension = os.path.splitext(filename_with_ext)

        if extension not in ['.jpg', '.jpeg', '.png']:
            logging.exception("Invalid image file format")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file format")
        
        image_url = upload_image.move_file_from_temporary_to_permanent_container(source_container_name="temporary-images", dest_container_name="promotion-images", old_blob_name=filename_with_ext, new_blob_name=f"promotion-{db_promotion.uuid}" + extension)
        db_promotion.image_url = image_url

    db_promotion.updated_on = datetime.utcnow()

    try:
        db.commit()
    except Exception as e:
        if promotion_image_url is not None:
            upload_image.delete_blob("promotion-images", f"promotion-{db_promotion.uuid}" + extension)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_promotion)
    promotion = add_conference_to_promotion(db, db_promotion)
    return promotion

def delete_promotion(db: Session, promotion_id: str):
    db_promotion = db.query(models.Promotions).filter(models.Promotions.uuid == promotion_id).first()
    db.delete(db_promotion)
    db.commit()
    return True

def add_conference_to_promotion(db: Session, promotion):
    if isinstance(promotion,list):
        for p in promotion:
            p.conference_id = db.query(models.Conference).filter(models.Conference.id == p.conference_id).first().uuid
    else:
        promotion.conference_id = db.query(models.Conference).filter(models.Conference.id == promotion.conference_id).first().uuid
    return promotion