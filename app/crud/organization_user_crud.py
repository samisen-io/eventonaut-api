import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from app.crud import organization_crud, users_crud
from .. import models
from ..schemas import organization_user_schemas as schemas
from datetime import datetime

def get_organization_user(db: Session, organization_user_id: str):
    return db.query(models.Organization_User).filter(models.Organization_User.uuid == organization_user_id).first()

def get_organization_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Organization_User).offset(skip).limit(limit).all()

def get_organization_user_by_organization_id_and_user_id(db: Session, organization_id: int, user_id: int):
    return db.query(models.Organization_User).filter((models.Organization_User.organization_id == organization_id) & (models.Organization_User.user_id == user_id)).first()

def create_organization_user(db: Session, organization_user: schemas.Organization_UserCreate):
    organization = organization_crud.get_organization_by_id(db, organization_user.organization_id)
    user = users_crud.get_user_by_uuid(db, organization_user.user_id)
    
    organization_user_exist = get_organization_user_by_organization_id_and_user_id(db, organization.id, user.id)
    
    if organization_user_exist is not None:
        raise HTTPException(status_code=404, detail="Organization_user already exists")
    
    db_organization_user = models.Organization_User(**organization_user.model_dump())
    db_organization_user.created_on = db_organization_user.updated_on = datetime.utcnow()
    db_organization_user.uuid = "ous-" + str(uuid.uuid4())
    db_organization_user.organization_id = organization.id
    db_organization_user.user_id = user.id
    db.add(db_organization_user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    db.refresh(db_organization_user)
    return db_organization_user

def update_organization_user(db: Session, organization_user: schemas.Organization_UserUpdate):
    db_organization_user = get_organization_user(db, organization_user.id)
    
    organization = organization_crud.get_organization_by_id(db, organization_user.organization_id)
    user = users_crud.get_user_by_uuid(db, organization_user.user_id) 
    
    organization_user_exist = get_organization_user_by_organization_id_and_user_id(db, organization.id, user.id)
    
    if organization_user_exist is not None:
        raise HTTPException(status_code=404, detail="Organization_user already exists")
    
    if db_organization_user is None:
        raise HTTPException(status_code=404, detail="Organization user not found")
    db_organization_user.organization_id = organization.id
    db_organization_user.user_id = user.id
    db_organization_user.uuid = organization_user.id
    db_organization_user.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_organization_user)
    return db_organization_user

def delete_organization_user(db: Session, organization_user_id: str):
    db_organization_user = get_organization_user(db, organization_user_id)
    if db_organization_user is None:
        raise HTTPException(status_code=404, detail="Organization user not found")
    db.delete(db_organization_user)
    db.commit()
    return {"message": "Organization user deleted successfully"}