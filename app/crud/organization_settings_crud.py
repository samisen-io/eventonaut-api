from sqlalchemy import BigInteger
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models import OrganizationSettings
from ..schemas import organization_settings_schemas as schemas
import uuid
from datetime import datetime

def get_organization_settings(db: Session, organization_id: int):
    return db.query(OrganizationSettings).filter(OrganizationSettings.organization_id == organization_id).first()

def create_organization_settings(db: Session, organization_settings: schemas.OrganizationSettingsCreate, organization_id: int):
    org_settings_dict = organization_settings.model_dump()
    org_settings_dict.pop('organization_id')
    db_organization_settings = OrganizationSettings(**org_settings_dict)
    db_organization_settings.organization_id = organization_id
    db_organization_settings.uuid = 'ost-' + str(uuid.uuid4())
    db_organization_settings.created_on = db_organization_settings.updated_on = datetime.utcnow()
    db.add(db_organization_settings)
    db.commit()
    db.refresh(db_organization_settings)
    return db_organization_settings

def update_organization_settings(db: Session, db_organization_settings: OrganizationSettings, organization_settings: schemas.OrganizationSettingsUpdate):
    db_organization_settings.updated_on = datetime.utcnow()
    org_settings_dict = organization_settings.model_dump()
    org_settings_dict.pop('organization_id')
    for key, value in org_settings_dict.items():
        if value is not None:
            setattr(db_organization_settings, key, value)
    db.commit()
    db.refresh(db_organization_settings)
    return db_organization_settings

def delete_organization_settings(db: Session, db_organization_settings: OrganizationSettings):
    db.delete(db_organization_settings)
    db.commit()
    return True

def get_organization_settings_by_eventbrite_org_id(db: Session, eventbrite_org_id: str):
    return db.query(OrganizationSettings).filter(OrganizationSettings.event_brite_org_id == eventbrite_org_id).first()