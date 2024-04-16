from sqlalchemy.orm import Session
from fastapi import HTTPException, APIRouter, Depends, status
from ..schemas import organization_settings_schemas as schemas
from ..basicauth import basic_auth
from ..dependencies import get_db
from ..crud import organization_settings_crud as crud
from ..crud import organization_crud
import logging

router = APIRouter(tags=["organization_settings"])

@router.get("/organization_settings/{organization_id}", response_model=schemas.OrganizationSettings)
def get_organization_settings(organization_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    organization = organization_crud.get_organization_by_id(db, organization_id)
    if organization is None:
        logging.exception(f"Organization not found for organization_id: {organization_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    db_organization_settings = crud.get_organization_settings(db, organization.id)
    if db_organization_settings is None:
        logging.exception(f"Organization settings not found for organization_id: {organization_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization settings not found")
    logging.info(f"Organization settings found for organization_id: {organization_id}")
    db_organization_settings.organization_id = organization_id
    return db_organization_settings

@router.post("/organization_settings", response_model=schemas.OrganizationSettings, status_code=status.HTTP_201_CREATED)
def create_organization_settings(organization_settings: schemas.OrganizationSettingsCreate, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    organization = organization_crud.get_organization_by_id(db, organization_settings.organization_id)
    if organization is None:
        logging.exception(f"Organization not found for organization_id: {organization_settings.organization_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    db_organization_settings = crud.get_organization_settings(db, organization.id)
    if db_organization_settings is not None:
        logging.exception(f"Organization settings already exist for organization_id: {organization_settings.organization_id}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization settings already exist")
    logging.info(f"Creating organization settings for organization_id: {organization_settings.organization_id}")
    db_organization_settings = crud.create_organization_settings(db, organization_settings, organization.id)
    db_organization_settings.organization_id = organization_settings.organization_id
    return db_organization_settings

@router.put("/organization_settings", response_model=schemas.OrganizationSettings)
def update_organization_settings(organization_settings: schemas.OrganizationSettingsUpdate, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    organization = organization_crud.get_organization_by_id(db, organization_settings.organization_id)
    if organization is None:
        logging.exception(f"Organization not found for organization_id: {organization_settings.organization_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    db_organization_settings = crud.get_organization_settings(db, organization.id)
    if db_organization_settings is None:
        logging.exception(f"Organization settings not found for organization_id: {organization_settings.organization_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization settings not found")
    logging.info(f"Updating organization settings for organization_id: {organization_settings.organization_id}")
    updated_organization_settings = crud.update_organization_settings(db, db_organization_settings, organization_settings)
    updated_organization_settings.organization_id = organization_settings.organization_id
    return updated_organization_settings

@router.delete("/organization_settings/{organization_id}")
def delete_organization_settings(organization_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    organization = organization_crud.get_organization_by_id(db, organization_id)
    if organization is None:
        logging.exception(f"Organization not found for organization_id: {organization_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    db_organization_settings = crud.get_organization_settings(db, organization.id)
    if db_organization_settings is None:
        logging.exception(f"Organization settings not found for organization_id: {organization_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization settings not found")
    logging.info(f"Deleting organization settings for organization_id: {organization_id}")
    return crud.delete_organization_settings(db, db_organization_settings)