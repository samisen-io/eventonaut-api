from fastapi import APIRouter, HTTPException, Depends, Security, status
import logging
from sqlalchemy.orm import Session
from app.schemas.user_schemas import UserAuthentication as User
from app.oauth2 import get_current_active_user
from app.static_enums.role import RoleEnum
from ..schemas import settings_schemas as schemas
from ..schemas import user_schemas as uschemas
from ..crud import settings_crud as crud, conferences_crud
from .. import basicauth
from ..dependencies import get_db

router = APIRouter(tags=["settings"])

# create settings by conference id and take body as any valid JSON and convert it to string
@router.post("/settings", response_model=schemas.Settings, status_code=status.HTTP_201_CREATED)
def create_settings(settings:schemas.SettingsCreate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    if conferences_crud.get_conference_by_uuid(db, uuid=settings.conference_id,owner_id=current_user.id) is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    db_settings = crud.get_settings_by_conference_uuid(db, conference_uuid=settings.conference_id,owner_id=current_user.id)
    if db_settings:
        logging.exception("Settings already exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Settings already exists")
    if settings.body is None or len(settings.body) == 0:
        logging.exception("Body is empty")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Body is empty")
    settings = crud.create_settings(db=db, settings=settings, owner_id=current_user.id)
    logging.info("Settings created for conference id: " + settings.conference_id)
    return settings

# get all settings
@router.get("/settings/all_settings", response_model=list[schemas.Settings])
def get_settings(db: Session = Depends(get_db), offset: int = 0, limit: int = 100):
    settings = crud.get_settings(db, offset=offset, limit=limit)
    if settings is None or len(settings) == 0:
        logging.exception("Settings not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not found")
    logging.info("All Settings retrieved")
    return settings

# get settings by conference id
@router.get("/settings/{conference_id}", response_model=schemas.Settings)
def get_settings_by_conference_id(conference_id: str, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    if conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id) is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    settings = crud.get_settings_by_conf_uuid(db, conference_uuid=conference_id)
    if settings is None:
        logging.exception("Settings not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not found")
    logging.info("Settings retrieved by conference id: " + conference_id)
    return settings

# update settings by conference id and settings id
@router.put("/settings", response_model=schemas.Settings)
def update_settings(settings: schemas.SettingsCreate,db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    if conferences_crud.get_conference_by_uuid(db, uuid=settings.conference_id,owner_id=current_user.id) is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    db_settings = crud.get_settings_by_conference_uuid(db, conference_uuid=settings.conference_id,owner_id=current_user.id)
    if db_settings is None:
        logging.exception("Settings not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not found")
    if settings.body is None or len(settings.body) == 0:
        logging.exception("Body is empty")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Body is empty")
    settings=crud.update_settings(db=db, settings=settings, owner_id=current_user.id)
    logging.info("Settings updated for conference: " + settings.conference_id)
    return settings

# delete settings by conference id and settings id
@router.delete("/settings/{conference_id}")
def delete_settings(conference_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    db_settings = crud.get_settings_by_conference_uuid(db, conference_uuid=conference_id,owner_id=current_user.id)
    if db_settings is None:
        logging.exception("Settings not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Settings not found")
    deleted_settings = crud.delete_settings(db=db, conference_uuid=conference_id, owner_id=current_user.id)
    logging.info("Settings deleted for conference: " + conference_id)
    return deleted_settings