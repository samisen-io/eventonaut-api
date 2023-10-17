from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..dependencies import get_db
from datetime import datetime, date
import json
import pytz

router = APIRouter(tags=["settings"])

# create settings by conference id and take body as any valid JSON and convert it to string
@router.post("/conference/{conference_id}", response_model=schemas.Settings)
def create_settings(conference_id: int, body: dict, db: Session = Depends(get_db)):
    db_settings = crud.get_settings_by_conference_id(db, conference_id=conference_id)
    if db_settings:
        raise HTTPException(status_code=400, detail="Settings already exists")
    if body is None or len(body) == 0:
        raise HTTPException(status_code=400, detail="Body is empty")
    return crud.create_settings(db=db, body=body, conference_id=conference_id)

# get all settings
@router.get("/settings", response_model=list[schemas.Settings])
def read_settings(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    settings = crud.get_settings(db, skip=skip, limit=limit)
    if settings is None or len(settings) == 0:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

# get settings by id
@router.get("/settings/{settings_id}")
def read_settings_by_id(settings_id: int, db: Session = Depends(get_db)):
    if settings_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid settings id")
    settings = crud.get_settings_by_id(db, settings_id=settings_id)
    if settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

# get settings by conference id
@router.get("/settings/conference/{conference_id}", response_model=schemas.Settings)
def read_settings_by_conference_id(conference_id: int, db: Session = Depends(get_db)):
    if conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference id")
    settings = crud.get_settings_by_conference_id(db, conference_id=conference_id)
    if settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    return settings

# update settings by conference id and settings id
@router.put("/conference/{conference_id}", response_model=schemas.Settings)
def update_settings(conference_id: int, body: dict, db: Session = Depends(get_db)):
    db_settings = crud.get_settings_by_conference_id(db, conference_id=conference_id)
    if db_settings is None:
        raise HTTPException(status_code=404, detail="No such conference exists")
    if body is None or len(body) == 0:
        raise HTTPException(status_code=400, detail="Body is empty")
    return crud.update_settings(db=db, body=body, conference_id=conference_id)

# delete settings by conference id and settings id
@router.delete("/conference/{conference_id}")
def delete_settings(conference_id: int, db: Session = Depends(get_db)):
    db_settings = crud.get_settings_by_conference_id(db, conference_id=conference_id)
    if db_settings is None:
        raise HTTPException(status_code=404, detail="Settings not found")
    return crud.delete_settings(db=db, conference_id=conference_id)