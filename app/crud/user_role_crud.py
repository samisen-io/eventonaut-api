from sqlalchemy.orm import Session
from .. import models
from ..schemas import user_role as schemas
import uuid
from datetime import datetime

def get_user_role(db: Session, user_role_id: int):
    return db.query(models.User_Role).filter(models.User_Role.id == user_role_id).first()

def get_user_role_by_user_id_and_role_id(db: Session, user_id: int, role_id: int):
    return db.query(models.User_Role).filter(models.User_Role.user_id == user_id, models.User_Role.role_id == role_id).first()

def get_user_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User_Role).offset(skip).limit(limit).all()

def create_user_role(db: Session, user_id: int, role_id: int):
    db_user_role = models.User_Role(user_id=user_id, role_id=role_id)
    db_user_role.uuid = "uro-" + str(uuid.uuid4())
    db_user_role.created_on = db_user_role.updated_on = datetime.utcnow()
    db.add(db_user_role)
    db.commit()
    db.refresh(db_user_role)
    return db_user_role

def update_user_role(db: Session, user_role: schemas.UserRoleUpdate, user_role_id: int):
    db_user_role = get_user_role(db, user_role_id)
    if db_user_role is None:
        return None
    for var, value in vars(user_role).items():
        setattr(db_user_role, var, value) if value else None
    db.add(db_user_role)
    db.commit()
    db.refresh(db_user_role)
    return db_user_role

def update_user_role_by_user_id_and_role_id(db: Session, user_role: schemas.UserRoleUpdate, user_id: int, role_id: int):
    db_user_role = get_user_role_by_user_id_and_role_id(db = db , user_id = user_id, role_id = role_id)
    if db_user_role is None:
        return None
    for var, value in vars(user_role).items():
        setattr(db_user_role, var, value) if value else None
    db.add(db_user_role)
    db.commit()
    db.refresh(db_user_role)
    return db_user_role

def delete_user_role(db: Session, user_role_id: int):
    db_user_role = get_user_role(db, user_role_id)
    if db_user_role is None:
        return None
    db.delete(db_user_role)
    db.commit()
    return db_user_role

def delete_user_role_by_user_and_role(db: Session, user_id: int, role_id: int):
    db_user_role = db.query(models.User_Role).filter(models.User_Role.user_id == user_id, models.User_Role.role_id == role_id).first()
    if db_user_role is None:
        return None
    db.delete(db_user_role)
    db.commit()
    return db_user_role