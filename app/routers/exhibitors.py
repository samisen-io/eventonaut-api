from ..dependencies import get_db
from ..schemas import exhibitor_schemas as schemas
from ..crud import exhibitor_crud as crud, conferences_crud as conf_crud
from ..crud import users_crud
from fastapi import APIRouter, Depends, HTTPException, status, Security
import logging
from ..oauth2 import get_current_active_user, get_current_active_organization
from ..static_enums.role import RoleEnum
from ..schemas.user_schemas import UserAuthentication as User
from ..schemas.organization_schemas import OrganizationSecurity
from email_validator import validate_email, EmailNotValidError

router = APIRouter(tags=["Exhibitors"])

@router.get("/exhibitor", response_model=list[schemas.ExhibitorResponse])
def get_exhibitors(db = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    exhibitors = crud.get_exhibitors_by_organization_id(db, current_organization.id)
    if not exhibitors or len(exhibitors) == 0:
        logging.exception(f"No exhibitors found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No exhibitors found")
    return exhibitors

@router.get("/exhibitors/{conference_id}", response_model=list[schemas.ExhibitorResponse])
def get_exhibitors(conference_id: str, db = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, RoleEnum.ATTENDEE.name])):
    roles = [user_role.role for user_role in current_user.user_roles]
    if roles[0].name == RoleEnum.ATTENDEE.name:
        conference = conf_crud.get_conference(db, conference_id)
    elif roles[0].name == RoleEnum.ORGANIZATION_ADMIN.name or roles[0].name == RoleEnum.ORGANIZATION_USER.name:
        organization_id = current_user.organization_user[0].organization_id
        conference = conf_crud.get_conference_by_id_for_organization(db, conference_id, organization_id)
    if not conference:
        logging.exception(f"Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    exhibitors = crud.get_exhibitors(db, conference.id)
    if not exhibitors or len(exhibitors) == 0:
        logging.exception(f"No exhibitors found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No exhibitors found")
    return exhibitors

@router.get("/exhibitor/{exhibitor_id}", response_model=schemas.ExhibitorResponse)
def get_exhibitor(exhibitor_id: str, db = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    organization_id = current_user.organization_user[0].organization_id
    exhibitor = crud.get_exhibitor_by_id(db, exhibitor_id, organization_id)
    if not exhibitor:
        logging.exception(f"Exhibitor not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibitor not found")
    return exhibitor

@router.post("/exhibitor", response_model=schemas.ExhibitorResponse, status_code=status.HTTP_201_CREATED)
def create_exhibitor(exhibitor: schemas.ExhibitorCreate, db = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    organization_id = current_user.organization_user[0].organization_id
    try:
        valid = validate_email(exhibitor.contact_email)
        exhibitor.contact_email = valid.normalized.lower()
    except EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    result = crud.create_exhibitor(db, exhibitor, organization_id)
    save_audit_log(db, "create", "exhibitor", organization_id, current_user.id, None, result)
    return result

@router.put("/exhibitor", response_model=schemas.ExhibitorResponse)
def update_exhibitor(exhibitor: schemas.ExhibitorUpdate, db = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    organization_id = current_user.organization_user[0].organization_id
    db_exhibitor = crud.get_exhibitor_by_id(db, exhibitor.id, organization_id)
    if not db_exhibitor:
        logging.exception(f"Exhibitor not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibitor not found")
    result = crud.update_exhibitor(db, db_exhibitor, exhibitor)
    save_audit_log(db, "update", "exhibitor", organization_id, current_user.id, db_exhibitor, result)
    return result

@router.delete("/exhibitor/{exhibitor_id}")
def delete_exhibitor(exhibitor_id: str, db = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    organization_id = current_user.organization_user[0].organization_id
    db_exhibitor = crud.get_exhibitor_by_id(db, exhibitor_id, organization_id)
    if not db_exhibitor:
        logging.exception(f"Exhibitor not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibitor not found") 
    result =  crud.delete_exhibitor(db, db_exhibitor)
    save_audit_log(db, "delete", "exhibitor", organization_id, current_user.id, db_exhibitor, None)
    return result
    
def save_audit_log(db, operation, table, organization_id, user_id=None, old_value=None, new_value=None):
    print(f"user_id: {user_id} of organization {organization_id} performed {operation} on a {table} table. old value: {old_value}, new value: {new_value}")