from .. import models
from ..schemas import promotion_schemas
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

def get_promotion(db: Session, promotion_id: str):
    return db.query(models.Promotions).filter(models.Promotions.uuid == promotion_id).first()

def get_promotion_by_conference(db: Session, conference_id: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id).first()
    return db.query(models.Promotions).filter(models.Promotions.conference_id == conference.id).first()

def get_promotions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Promotions).order_by(models.Promotions.rank).offset(skip).limit(limit).all()

def get_all_promotions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Promotions).offset(skip).limit(limit).all()

def create_promotion(db: Session, promotion: promotion_schemas.PromotionCreate):
    db_promotion = models.Promotions(**promotion.model_dump())
    db_promotion.uuid = "pro-" + str(uuid.uuid4())
    db_promotion.created_on = db_promotion.updated_on = datetime.utcnow()
    db_promotion.conference_id = db.query(models.Conference).filter(models.Conference.uuid == promotion.conference_id).first().id
    db.add(db_promotion)
    db.commit()
    db.refresh(db_promotion)
    return db_promotion

def update_promotion(db: Session, promotion: promotion_schemas.PromotionUpdate):
    db_promotion = db.query(models.Promotions).filter(models.Promotions.uuid == promotion.id).first()
    promotion: dict = promotion.model_dump()
    promotion_rank = promotion.pop('rank')
    promotion.pop('id')
    updates = promotion
    for key, value in updates.items():
        if value is not None:
            setattr(db_promotion, key, value)

    if promotion_rank != 0:
        db_promotion.rank = promotion_rank

    db_promotion.updated_on = datetime.utcnow()

    db.commit()
    db.refresh(db_promotion)
    return db_promotion

def delete_promotion(db: Session, promotion_id: str):
    db_promotion = db.query(models.Promotions).filter(models.Promotions.uuid == promotion_id).first()
    db.delete(db_promotion)
    db.commit()
    return True