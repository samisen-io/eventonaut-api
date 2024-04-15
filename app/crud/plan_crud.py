from sqlalchemy.orm import Session
from .. import models
from ..schemas import plan_schemas as schemas
from fastapi import HTTPException
from datetime import datetime
import uuid

def get_plans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Plan).offset(skip).limit(limit).all()

def get_plan_by_plan_id(db: Session, plan_id: str):
    return db.query(models.Plan).filter(models.Plan.plan_id == plan_id).first()

def get_plan_by_uuid(db: Session, uuid: str):
    return db.query(models.Plan).filter(models.Plan.uuid == uuid).first()

def create_plan(db: Session, plan: schemas.PlanCreate):
    db_plan = models.Plan(**plan.model_dump())
    db_plan.uuid = "pln-" + str(uuid.uuid4())
    db_plan.created_on = db_plan.updated_on = datetime.utcnow()
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan

def update_plan(db: Session, update_plan: schemas.PlanUpdate, db_plan: models.Plan):
    update_plan = update_plan.model_dump()
    for key, value in update_plan.items():
        if value is not None:
            setattr(db_plan, key, value)
    db_plan.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_plan)
    return db_plan

def delete_plan(db: Session, db_plan: models.Plan):
    db.delete(db_plan)
    db.commit()
    return db_plan