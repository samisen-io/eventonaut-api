import logging

from sqlalchemy import text
from app.routers import upload_image
from .. import models
from ..schemas import promotion_schemas
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
from fastapi import HTTPException, status
from ..static_enums.blob_container_enums import BlobContainer
from sqlalchemy.orm import joinedload
import time

def get_promotion(db: Session, promotion_id: str):
    promotion = db.query(models.Promotions).options(joinedload(models.Promotions.conference)).filter(models.Promotions.uuid == promotion_id).first()
    return promotion

def get_promotion_by_conference(db: Session, conference_id: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id).first()
    return None if conference is None else db.query(models.Promotions).filter(models.Promotions.conference_id == conference.id).first()

def get_promotions(db: Session, skip: int = 0, limit: int = 5):
    return db.query(models.Promotions).options(joinedload(models.Promotions.conference)).order_by(models.Promotions.rank, models.Promotions.updated_on.desc()).offset(skip).limit(limit).all()

def get_all_promotions(db: Session, skip: int = 0, limit: int = 100):
    promotions = db.query(models.Promotions).options(joinedload(models.Promotions.conference)).order_by(models.Promotions.rank, models.Promotions.updated_on.desc()).offset(skip).limit(limit).all()
    return promotions

def create_promotion(db: Session, promotion: promotion_schemas.PromotionCreate):
    db_promotion = models.Promotions(**promotion.model_dump())
    db_promotion.uuid = "pro-" + str(uuid.uuid4())
    db_promotion.created_on = db_promotion.updated_on = datetime.utcnow()
    conference = db.query(models.Conference).filter(models.Conference.uuid == promotion.conference_id).first()
    db_promotion.conference_id = conference.id
    
    try:
        db_promotion.image_url = upload_image.get_actual_url(image_url=promotion.image_url, new_blob_container=BlobContainer.PROMOTION_IMAGES.value, new_blob_name=f"promotion-{db_promotion.uuid}")
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    db.add(db_promotion)
    try:
        db.commit()
    except Exception as e:
        upload_image.delete_blob_by_url(db_promotion.image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_promotion)
    promotion = db.query(models.Promotions).options(joinedload(models.Promotions.conference)).filter(models.Promotions.uuid == db_promotion.uuid).first()
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

    if promotion_image_url is not None and upload_image.get_actual_url(image_url=promotion_image_url) != db_promotion.image_url:
        db_promotion.image_url = upload_image.get_actual_url(image_url=promotion_image_url, new_blob_container="promotion-images", new_blob_name=f"promotion-{db_promotion.uuid}")

    db_promotion.updated_on = datetime.utcnow()

    try:
        db.commit()
    except Exception as e:
        if promotion_image_url is not None:
            upload_image.delete_blob_by_url(db_promotion.image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_promotion)
    promotion = db.query(models.Promotions).options(joinedload(models.Promotions.conference)).filter(models.Promotions.uuid == db_promotion.uuid).first()
    return promotion

def delete_promotion(db: Session, promotion_id: str):
    db_promotion = db.query(models.Promotions).filter(models.Promotions.uuid == promotion_id).first()
    db.delete(db_promotion)
    db.commit()
    return True