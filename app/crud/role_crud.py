import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from .. import models
from ..schemas import role_schemas as schemas


def get_role(db: Session, role_id: str):
    return db.query(models.Role).filter(models.Role.uuid == role_id).first()


def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Role).offset(skip).limit(limit).all()


def create_role(db: Session, role: schemas.RoleCreate):
    try:
        db_role = models.Role(**role.model_dump())
        db_role.uuid = "rol-" + str(uuid.uuid4())
        db_role.created_on = db_role.updated_on = datetime.utcnow()
        db.add(db_role)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            return "Cant create role. Error occurred: " + str(e)
        db.refresh(db_role)
        return db_role
    except Exception as e:
        print(f"Error occurred: {str(e)}")


def update_role(db: Session, role: schemas.RoleUpdate):
    db_role = get_role(db, role.id)
    if role.name is not None:
        db_role.name = role.name
    if role.description is not None:
        db_role.description = role.description
    db_role.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_role)
    return db_role


def delete_role(db: Session, role_id: str):
    db_role = get_role(db, role_id)
    db.delete(db_role)
    db.commit()
    return {"message": "Role deleted successfully"}