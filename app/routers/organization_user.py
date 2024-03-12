from typing import List
from fastapi import APIRouter, HTTPException, Depends, Security
from app import basicauth

from app.oauth2 import get_current_active_user
from app.static_enums.role import RoleEnum
from ..crud import organization_user_crud as crud
from ..schemas import organization_user_schemas as schemas
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..dependencies import get_db
from ..basicauth import basic_auth

router = APIRouter(tags=["organization_user"])

def get_mapped_organization_user_response(organization_user):
    organization_user.organization_id = organization_user.organization.uuid
    organization_user.user_id = organization_user.user.uuid
    organization_user.id = organization_user.uuid
    return organization_user
     
@router.post("/organization_user", response_model=schemas.Organization_User)
def create_organization_user(organization_user: schemas.Organization_UserCreate, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name])):
    try:
        new_organization_user = crud.create_organization_user(db ,organization_user)
        return get_mapped_organization_user_response(new_organization_user)
    except Exception as exc:
        raise exc

@router.get("/organization_user/{id}", response_model=schemas.Organization_User)
def get_organization_user(organization_user_id: str, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name]), basic_auth = Depends(basic_auth)):
    try:
        organization_user = crud.get_organization_user(db, organization_user_id)
        if organization_user is None:
            raise HTTPException(status_code=404, detail="Organization user not found")
        return get_mapped_organization_user_response(organization_user)
    except Exception as exc:
        raise exc

@router.get("/organization_users", response_model=List[schemas.Organization_User])
def get_organization_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    try:
        organization_users = crud.get_organization_users(db, skip, limit)
        mapped_organization_users = [get_mapped_organization_user_response(organization_user) for organization_user in organization_users]
        return mapped_organization_users
    except Exception as exc:
        raise exc
    
@router.get("/organization_user/users/{organization_id}", response_model=schemas.OrganizationUsersResponse)
def get_users_by_organization_id(organization_id: str, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name])):
    response = crud.get_users_by_organization_uuid(db, organization_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return response

@router.get("/organization_user/organizations/{user_id}", response_model=schemas.UserOrganizationsResponse, include_in_schema=False)
def get_organizations_by_user_id(user_id: str, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    return crud.get_organizations_by_user_uuid(db, user_id) #TODO: Take the id from the token

@router.put("/organization_user/{id}", response_model=schemas.Organization_UserUpdate)
def update_organization_user(organization_user: schemas.Organization_UserUpdate, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name])):
    try:
        updated_organization_user = crud.update_organization_user(db=db, organization_user=organization_user)
        if updated_organization_user is None:
            raise HTTPException(status_code=404, detail="Organization user not found")
        return get_mapped_organization_user_response(updated_organization_user)
    except Exception as exc:
        raise exc

@router.delete("/organization_user/{id}", response_model=schemas.DeleteResponse)
def delete_organization_user(organization_user_id: str, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name])):
    try:
        crud.delete_organization_user(db, organization_user_id)
        return {"message": "Organization user deleted successfully"}
    except Exception as exc:
        raise exc
