from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..dependencies import get_db
from datetime import datetime

router = APIRouter(tags=["settings"])

# get all settings
# create settings by conference id
@router.post("/settings/conference/{conference_id}", response_model=schemas.Settings)
def create_settings(conference_id: int, settings: schemas.SettingsCreate, db: Session = Depends(get_db)):
    db_settings = crud.get_settings_by_conference_id(db, conference_id=conference_id)
    if db_settings:
        raise HTTPException(status_code=400, detail="Settings already exist")
    return crud.create_settings(db=db, settings=settings, conference_id=conference_id)

@router.get("/settings", response_model=list[schemas.Settings])
def read_settings(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    settings = crud.get_settings(db, skip=skip, limit=limit)
    if settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

# get settings by id
@router.get("/settings/{settings_id}", response_model=schemas.Settings)
def read_settings_by_id(settings_id: int, db: Session = Depends(get_db)):
    settings = crud.get_settings_by_id(db, settings_id=settings_id)
    if settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

# get settings by conference id
@router.get("/settings/conference/{conference_id}", response_model=schemas.Settings)
def read_settings_by_conference_id(conference_id: int, db: Session = Depends(get_db)):
    settings = crud.get_settings_by_conference_id(db, conference_id=conference_id)
    if settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

# update settings by conference id and settings id
@router.put("/settings/conference/{conference_id}/{settings_id}", response_model=schemas.Settings)
def update_settings(conference_id: int, settings_id: int, settings: schemas.SettingsCreate, db: Session = Depends(get_db)):
    db_settings = crud.get_settings_by_conference_id(db, conference_id=conference_id)
    if db_settings is None:
        raise HTTPException(status_code=404, detail="No such conference exists")
    db_settings = crud.get_settings_by_id(db, settings_id=settings_id)
    if db_settings is None:
        raise HTTPException(status_code=404, detail="No such settings exists")
    return crud.update_settings(db=db, settings=settings, conference_id=conference_id, settings_id=settings_id)

# delete settings by conference id and settings id
@router.delete("/settings/conference/{conference_id}/{settings_id}")
def delete_settings(conference_id: int, settings_id: int, db: Session = Depends(get_db)):
    db_settings = crud.get_settings_by_conference_id_settings_id(db, conference_id=conference_id, settings_id=settings_id)
    if db_settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    return crud.delete_settings(db=db, settings_id=settings_id, conference_id=conference_id)

# get all settings by conference id and created on
@router.get("/settings/conference/{conference_id}/{created_on}", response_model=list[schemas.Settings])
def read_settings_by_conference_id_created_on(conference_id: int, created_on: str, db: Session = Depends(get_db)):
    if len(created_on) == 8:
        try:
            date_str = str(datetime.strptime(created_on, '%d-%m-%y').date())
        except:
            raise HTTPException(status_code=400, detail="Invalid Date Format")
    elif len(created_on) == 10:
        try:
            date_str = str(datetime.strptime(created_on, '%d-%m-%Y').date())
        except:
            raise HTTPException(status_code=400, detail="Invalid Date Format")
    else:
        raise HTTPException(status_code=400, detail="Invalid Date Format")
    settings = crud.get_settings_by_created_on_conference_id_date(db, conference_id=conference_id, created_on=date_str)
    if settings is None or len(settings) == 0:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

# get all settings by conference id and updated on
@router.get("/settings/conference/{conference_id}/{updated_on}", response_model=list[schemas.Settings])
def read_settings_by_conference_id_updated_on(conference_id: int, updated_on: str, db: Session = Depends(get_db)):
    if len(updated_on) == 8:
        try:
            date_str = str(datetime.strptime(updated_on, '%d-%m-%y').date())
        except:
            raise HTTPException(status_code=400, detail="Invalid Date Format")
    elif len(updated_on) == 10:
        try:
            date_str = str(datetime.strptime(updated_on, '%d-%m-%Y').date())
        except:
            raise HTTPException(status_code=400, detail="Invalid Date Format")
    else:
        raise HTTPException(status_code=400, detail="Invalid Date Format")
    settings = crud.get_settings_by_updated_on_conference_id_date(db, conference_id=conference_id, updated_on=date_str)
    if settings is None or len(settings) == 0:
        raise HTTPException(status_code=404, detail="Settings not found")
    return len(date_str)