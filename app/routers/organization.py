from typing import List
from fastapi import APIRouter, HTTPException, Depends, Security
from sqlalchemy.orm import Session

from app.oauth2 import get_current_active_user
from app.static_enums.role import RoleEnum
from ..crud import organization_crud as crud
from ..schemas import organization_schemas as schemas
from ..database import SessionLocal
from ..dependencies import get_db
from ..models import Organization

router = APIRouter(tags=['organizations'])

@router.post("/organizations/", response_model=schemas.Organization)
def create_organization(organization: schemas.OrganizationCreate, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name])):
    result = crud.create_organization(db=db, organization=organization)
    save_audit_log(db, "create", "organization", result.id, User.id, None, result)
    return result

@router.get("/organizations/", response_model=List[schemas.Organization])
def get_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name])):
    try:
        organizations = crud.get_all_organizations(db, skip, limit)
        return organizations
    except Exception as exc:
        raise exc
    
@router.get("/organizations/{id}", response_model=schemas.Organization)
def get_organization(organization_id: str, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name])):
    db_organization = crud.get_organization_by_uuid(db, organization_uuid=organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization

@router.put("/organizations/", response_model=schemas.Organization)
def update_organization(organization: schemas.OrganizationUpdate, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name])):
    db_organization = crud.get_organization_by_uuid(db, organization_uuid=organization.id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    save_audit_log(db, "update", "organization", organization.id, User.id, db_organization, organization)
    return crud.update_organization(db=db, organization=organization, db_organization=db_organization)

@router.delete("/organizations/{id}")
def delete_organization(organization_id: str, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name])):
    db_organization = crud.get_organization_by_uuid(db, organization_uuid=organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    crud.delete_organization(db=db, db_organization=db_organization)
    save_audit_log(db, "delete", "organization", organization_id, User.id, db_organization, None)
    return {"detail": "Organization deleted"}

def save_audit_log(db, operation, table, organization_id, user_id=None, old_value=None, new_value=None):
    print(f"user_id: {user_id} of organization {organization_id} performed {operation} on a {table} table. old value: {old_value}, new value: {new_value}")