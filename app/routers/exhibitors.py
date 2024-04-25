from ..dependencies import get_db
from ..schemas import exhibitor_schemas as schemas
from ..crud import exhibitor_crud as crud, conferences_crud as conf_crud
from ..crud import users_crud
from fastapi import APIRouter, Depends, HTTPException, status, Security
import logging
from ..oauth2 import get_current_active_user
from ..static_enums.role import RoleEnum
from ..schemas.user_schemas import UserAuthentication as User

router = APIRouter(tags=["Exhibitors"])

@router.get("/exhibitors/{conference_id}", response_model=list[schemas.ExhibitorResponse])
def get_exhibitors(conference_id: str, db = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, RoleEnum.ATTENDEE.name])):
    roles = users_crud.get_role_by_user_id(db, current_user.id)
    if roles[0].name == RoleEnum.ATTENDEE.name:
        conference = conf_crud.get_conference(db, conference_id)
    elif roles[0].name == RoleEnum.ORGANIZATION_ADMIN.name or roles[0].role_name == RoleEnum.ORGANIZATION_USER.name:
        conference = conf_crud.get_conference_by_uuid(db, conference_id, current_user.id)
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
    exhibitor = crud.get_exhibitor_by_id(db, exhibitor_id)
    if not exhibitor:
        logging.exception(f"Exhibitor not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibitor not found")
    return exhibitor

@router.post("/exhibitor", response_model=schemas.ExhibitorResponse, status_code=status.HTTP_201_CREATED)
def create_exhibitor(exhibitor: schemas.ExhibitorCreate, db = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    conference = conf_crud.get_conference_by_uuid(db, exhibitor.conference_id, current_user.id)
    if not conference:
        logging.exception(f"Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    return crud.create_exhibitor(db, exhibitor, conference.id)

@router.put("/exhibitor", response_model=schemas.ExhibitorResponse)
def update_exhibitor(exhibitor: schemas.ExhibitorUpdate, db = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    db_exhibitor = crud.get_exhibitor_by_id(db, exhibitor.id)
    if not db_exhibitor:
        logging.exception(f"Exhibitor not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibitor not found")
    if exhibitor.conference_id:
        db_conference = conf_crud.get_conference_by_uuid(db, exhibitor.conference_id, current_user.id)
        if not db_conference:
            logging.exception(f"Conference not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    return crud.update_exhibitor(db, db_exhibitor, exhibitor, db_conference.id if exhibitor.conference_id else None)

@router.delete("/exhibitor/{exhibitor_id}")
def delete_exhibitor(exhibitor_id: str, db = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    db_exhibitor = crud.get_exhibitor_by_id(db, exhibitor_id)
    if not db_exhibitor:
        logging.exception(f"Exhibitor not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibitor not found")
    return crud.delete_exhibitor(db, db_exhibitor)
    