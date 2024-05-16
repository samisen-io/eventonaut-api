from sqlalchemy.orm import Session
from fastapi import HTTPException, APIRouter, Depends, status, Security

from app.eventbrite_operations import get_organization_id
from ..schemas import organization_settings_schemas as schemas
from ..basicauth import basic_auth
from ..dependencies import get_db
from ..crud import organization_settings_crud as crud
from ..crud import organization_crud
import logging
from ..oauth2 import get_current_active_organization
from ..static_enums.role import RoleEnum
from ..schemas.organization_schemas import Organization

router = APIRouter(tags=["organization_settings"])

@router.get("/organization_settings", response_model=schemas.OrganizationSettings)
def get_organization_settings(db: Session = Depends(get_db), current_organization: Organization = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    organization = organization_crud.get_organization_by_id(db, current_organization.id)
    if organization is None:
        logging.exception(f"Organization not found for organization_id: {current_organization.uuid}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    db_organization_settings = crud.get_organization_settings(db, organization.id)
    if db_organization_settings is None:
        logging.exception(f"Organization settings not found for organization_id: {organization.uuid}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization settings not found")
    logging.info(f"Organization settings found for organization_id: {organization.uuid}")
    db_organization_settings.organization_id = organization.uuid
    return db_organization_settings

@router.post("/organization_settings", response_model=schemas.OrganizationSettings, status_code=status.HTTP_201_CREATED)
def create_organization_settings(organization_settings: schemas.OrganizationSettingsCreate, db: Session = Depends(get_db), current_organization: Organization = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    organization = organization_crud.get_organization_by_id(db, current_organization.id)
    if organization is None:
        logging.exception(f"Organization not found for organization_id: {current_organization.uuid}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    db_organization_settings = crud.get_organization_settings(db, organization.id)
    # print(db_organization_settings.event_brite_access_token)
    # print(db_organization_settings.organization_id)
    evt_brite_org_id = get_organization_id(organization_settings.event_brite_access_token)
    if db_organization_settings is not None:
        logging.exception(f"Organization settings already exist for organization_id: {organization.uuid}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization settings already exist")
    logging.info(f"Creating organization settings for organization_id: {organization.uuid}")
    db_organization_settings = crud.create_organization_settings(db, organization_settings, organization.id, evt_brite_org_id)
    db_organization_settings.organization_id = organization.uuid
    save_audit_log(db, "create", "organization_settings", organization.id, None, None, db_organization_settings)
    return db_organization_settings

@router.put("/organization_settings", response_model=schemas.OrganizationSettings)
def update_organization_settings(organization_settings: schemas.OrganizationSettingsUpdate, db: Session = Depends(get_db), current_organization: Organization = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    organization = organization_crud.get_organization_by_id(db, current_organization.id)
    if organization is None:
        logging.exception(f"Organization not found for organization_id: {current_organization.uuid}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    db_organization_settings = crud.get_organization_settings(db, organization.id)
    if db_organization_settings is None:
        logging.exception(f"Organization settings not found for organization_id: {organization.uuid}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization settings not found")
    logging.info(f"Updating organization settings for organization_id: {organization.uuid}")
    evt_brite_org_id = get_organization_id(organization_settings.event_brite_access_token)
    updated_organization_settings = crud.update_organization_settings(db, db_organization_settings, organization_settings, evt_brite_org_id)
    updated_organization_settings.organization_id = organization.uuid
    save_audit_log(db, "update", organization.id, "organization_settings", db_organization_settings, updated_organization_settings)
    return updated_organization_settings

@router.delete("/organization_settings")
def delete_organization_settings(db: Session = Depends(get_db), current_organization: Organization = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    organization = organization_crud.get_organization_by_id(db, current_organization.id)
    if organization is None:
        logging.exception(f"Organization not found for organization_id: {current_organization.uuid}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    db_organization_settings = crud.get_organization_settings(db, organization.id)
    if db_organization_settings is None:
        logging.exception(f"Organization settings not found for organization_id: {organization.uuid}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization settings not found")
    logging.info(f"Deleting organization settings for organization_id: {organization.uuid}")
    result = crud.delete_organization_settings(db, db_organization_settings)
    save_audit_log(db, "delete", "organization_settings", organization.id, None, db_organization_settings, None)
    return result

def save_audit_log(db, operation, table, organization_id, user_id=None, old_value=None, new_value=None):
    print(f"user_id: {user_id} of organization {organization_id} performed {operation} on a {table} table. old value: {old_value}, new value: {new_value}")