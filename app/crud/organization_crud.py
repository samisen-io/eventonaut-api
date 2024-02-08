from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..schemas import organization_schemas
from .. import models
import uuid
from datetime import datetime
from fastapi import HTTPException
from pydantic import ValidationError

def get_all_organizations(db: Session, offset: int, limit: int):
    try:
        return db.query(models.Organization).offset(offset).limit(limit).all()
    except Exception as e:
        raise e

def get_organization_by_id(db: Session, organization_id: str):
    return db.query(models.Organization).filter(models.Organization.uuid == organization_id).first()

def create_organization(db: Session, organization: organization_schemas.OrganizationCreate):
    try:
        db_organization = models.Organization(**organization.model_dump())
        db_organization.created_on = db_organization.updated_on = datetime.utcnow()
        db_organization.uuid = 'org-' + str(uuid.uuid4())
        db.add(db_organization)
        db.commit()
        db.refresh(db_organization)
        return db_organization

    except Exception as e:
        raise e

def update_organization(db: Session, organization: organization_schemas.OrganizationUpdate, db_organization: models.Organization):
    organization_dict = organization.model_dump()
    organization_dict.pop('id')

    for key, value in organization_dict.items():
        if value is not None:
            setattr(db_organization, key, value)

    db_organization.updated_on = datetime.utcnow()

    db.commit()
    db.refresh(db_organization)
    return db_organization

def delete_organization(db: Session, db_organization: models.Organization):
    db.delete(db_organization)
    db.commit()
    return True