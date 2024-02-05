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
    db_role = models.Role(
        name=role.name,
        uuid="rol-" + str(uuid.uuid4()),
        created_on=datetime.utcnow(),
        updated_on=datetime.utcnow(),
        description=role.description,
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


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