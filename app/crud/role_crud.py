import uuid
from datetime import datetime
from fastapi import HTTPException, status

from sqlalchemy.orm import Session

from .. import models
from ..schemas import role_schemas as schemas


def get_role(db: Session, role_name: str):
    return db.query(models.Role).filter(models.Role.name.ilike(role_name)).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Role).offset(skip).limit(limit).all()

def is_role_name_unique(db: Session, role_name: str):
    db_role = get_role(db, role_name.upper())
    return db_role is None

def create_role(db: Session, role: schemas.RoleCreate):
    try:
        if not is_role_name_unique(db, role.name.upper()):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name already exists")
        
        db_role = models.Role(**role.model_dump())
        db_role.uuid = "rol-" + str(uuid.uuid4())
        db_role.created_on = db_role.updated_on = datetime.utcnow()
        db.add(db_role)
        try:
            db.commit()
        except HTTPException as e:
            db.rollback()
            raise e
        db.refresh(db_role)
        return db_role
    except HTTPException as e:
        raise e


def update_role(db: Session, role: schemas.RoleUpdate):  
    if role.name is None:
        raise HTTPException(status_code=400, detail="Role name cannot be empty")
    
    db_role = get_role(db, role.name)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if role.description is not None:
        db_role.description = role.description
    
    db_role.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_name: str):
    db_role = get_role(db, role_name)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(db_role)
    db.commit()
    return {"message": "Role deleted successfully"}