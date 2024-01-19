from .. import models
from ..schemas import promotion_schemas
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

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
    db.add(db_promotion)
    db.commit()
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
    promotion.pop('id')
    updates = promotion
    for key, value in updates.items():
        if value is not None:
            setattr(db_promotion, key, value)

    if promotion_rank != 0:
        db_promotion.rank = promotion_rank

    if conference_id is not None:
        db_conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id).first()
        db_promotion.conference_id = db_conference.id
        promotion.location = db_conference.location

    db_promotion.updated_on = datetime.utcnow()

    db.commit()
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