from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.oauth2 import get_current_active_user
from ..schemas import settings_schemas as schemas
from ..schemas import user_schemas as uschemas
from ..crud import settings_crud as crud, conferences_crud
from ..dependencies import get_db

router = APIRouter(tags=["settings"])

# create settings by conference id and take body as any valid JSON and convert it to string
@router.post("/settings", response_model=schemas.Settings)
def create_settings(settings:schemas.SettingsCreate, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)):
    if conferences_crud.get_conference_by_uuid(db, uuid=settings.conference_id,owner_id=current_user.id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_settings = crud.get_settings_by_conference_uuid(db, conference_uuid=settings.conference_id,owner_id=current_user.id)
    if db_settings:
        raise HTTPException(status_code=400, detail="Settings already exists")
    if settings.body is None or len(settings.body) == 0:
        raise HTTPException(status_code=400, detail="Body is empty")
    return crud.create_settings(db=db, settings=settings, owner_id=current_user.id)

# get all settings
@router.get("/settings/all_settings", response_model=list[schemas.Settings])
def get_settings(db: Session = Depends(get_db), offset: int = 0, limit: int = 100):
    settings = crud.get_settings(db, offset=offset, limit=limit)
    if settings is None or len(settings) == 0:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

# get settings by conference id
@router.get("/settings/{conference_id}", response_model=schemas.Settings)
def get_settings_by_conference_id(conference_id: str, db: Session = Depends(get_db)):
    if conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    settings = crud.get_settings_by_conf_uuid(db, conference_uuid=conference_id)
    if settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

# update settings by conference id and settings id
@router.put("/settings", response_model=schemas.Settings)
def update_settings(settings: schemas.SettingsCreate,db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)):
    if conferences_crud.get_conference_by_uuid(db, uuid=settings.conference_id,owner_id=current_user.id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_settings = crud.get_settings_by_conference_uuid(db, conference_uuid=settings.conference_id,owner_id=current_user.id)
    if db_settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    if settings.body is None or len(settings.body) == 0:
        raise HTTPException(status_code=400, detail="Body is empty")
    settings=crud.update_settings(db=db, settings=settings, owner_id=current_user.id)
    return settings

# delete settings by conference id and settings id
@router.delete("/settings/{conference_id}")
def delete_settings(conference_id: str, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)):
    db_settings = crud.get_settings_by_conference_uuid(db, conference_uuid=conference_id,owner_id=current_user.id)
    if db_settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    return crud.delete_settings(db=db, conference_uuid=conference_id, owner_id=current_user.id)