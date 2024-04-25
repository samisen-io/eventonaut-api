from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..schemas import organization_schemas
from .. import models
import uuid
from datetime import datetime
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import joinedload
from sqlalchemy import text

def get_all_organizations(db: Session, offset: int, limit: int):
    try:
        return db.query(models.Organization).offset(offset).limit(limit).all()
    except Exception as e:
        raise e

def get_organization_by_uuid(db: Session, organization_uuid: str):
    return db.query(models.Organization).filter(models.Organization.uuid == organization_uuid).first()

def get_organization_by_id(db: Session, organization_id: int):
    return db.query(models.Organization).filter(models.Organization.id == organization_id).first()

def get_organization_by_name(db: Session, organization_name: str):
    return db.query(models.Organization).filter(models.Organization.name == organization_name).first()


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
        if 'unique constraint "ix_organization_name"' in str(e):
            raise HTTPException(status_code=400, detail="Organization name already in use") from e
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

# get organization by user id
def get_organization_by_user_id(db: Session, user_id: int):
    query = text("""
        SELECT organization.*
        FROM organization
        JOIN organization_user ON organization.id = organization_user.organization_id
        WHERE organization_user.user_id = :user_id
        LIMIT 1
    """)
    organization = db.execute(query, {"user_id": user_id}).first()
    return organization