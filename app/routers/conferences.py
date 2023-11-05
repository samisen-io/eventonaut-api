from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.oauth2 import get_current_active_user
from ..schemas import conference_schemas as schemas
from ..schemas import user_schemas as uschemas
from ..crud import conferences_crud as crud, users_crud
from ..dependencies import get_db
from .. encryption import encrypt_number, decrypt_number
from datetime import date
import uuid

router = APIRouter(tags=["conferences"])

# create conference
@router.post("/conferences", response_model=schemas.Conference)
def create_conference_for_user(conference: schemas.ConferenceCreate, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)):
    if current_user.id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user id")
    if not users_crud.get_user(db, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="User not found")
    if conference.start_date > conference.end_date or conference.start_date < date.today():
        raise HTTPException(status_code=400, detail="Invalid date range")
    conference=crud.create_user_conference(db=db, conference=conference, user_id=current_user.id)
    conference.id=encrypt_number(conference.id)
    conference.owner_id=encrypt_number(conference.owner_id)
    return conference

# get all conferences
@router.get("/conferences/all_conferences", response_model=list[schemas.Conference])
def get_all_conferences(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if skip < 0 or limit < 0:
        raise HTTPException(status_code=400, detail="Invalid query parameters")
    conferences = crud.get_conferences(db, skip=skip, limit=limit)
    if conferences is None or len(conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    for conference in conferences:
        conference.id=encrypt_number(conference.id)
        conference.owner_id=encrypt_number(conference.owner_id)
    return conferences

# get all conferences by owner_id
@router.get("/conferences", response_model=list[schemas.Conference])
def get_all_conferences_by_owner_id(db: Session = Depends(get_db),current_user: uschemas.User = Depends(get_current_active_user)):
    if current_user.id <= 0:
        raise HTTPException(status_code=400, detail="Invalid owner id")
    if users_crud.get_user(db, user_id=current_user.id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_conferences = crud.get_conferences_by_owner_id(db, owner_id=current_user.id)
    if db_conferences is None or len(db_conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

# update conference by conference id
@router.put("/conferences", response_model=schemas.Conference)
def update_conference(conference: schemas.ConferenceUpdate, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)):
    db_conference = crud.get_conference_by_uuid(db, uuid=conference.id, owner_id=current_user.id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    if conference.start_date is not None and conference.end_date is not None:
        if conference.start_date > conference.end_date or conference.start_date < date.today():
            raise HTTPException(status_code=400, detail="Invalid date range")
    return crud.update_user_conference(db=db, conference=conference, uuid=conference.id, owner_id=current_user.id)

# delete conference
@router.delete("/conferences/{conference_id}")
def delete_conference_owner_id_conference_id(conference_id: str, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)):
    if current_user.id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id")
    if not users_crud.get_user(db, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="User not found")
    db_conference = crud.get_conference_by_uuid(db,owner_id=current_user.id, uuid=conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return crud.delete_conference(db=db, owner_id=current_user.id, uuid=conference_id)