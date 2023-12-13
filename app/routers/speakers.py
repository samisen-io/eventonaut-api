from ..dependencies import get_db
from .. import models
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Security
from ..schemas import speaker_schemas as schemas
from ..crud import speakers_crud as crud, conferences_crud
from app.oauth2 import get_current_active_user
from app.schemas.user_schemas import UserAuthentication as User


router = APIRouter(tags=["speakers"])

@router.post("/speakers", response_model=schemas.Speaker)
def create_speaker(speaker: schemas.SpeakerCreate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    if conferences_crud.get_conference_by_uuid(db=db,uuid=speaker.conference_id,owner_id=current_user.id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return crud.create_speaker(db=db, speaker=speaker)

@router.get("/speakers", response_model=list[schemas.Speaker])
def get_all_speakers(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    speakers = crud.get_all_speakers(db, offset=offset, limit=limit)
    if speakers is None or len(speakers) == 0:
        raise HTTPException(status_code=404, detail="Speaker not found")
    return speakers

@router.get("/speakers/{speaker_id}", response_model=schemas.Speaker)
def get_speaker(speaker_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_speaker = crud.get_speaker(db, speaker_id=speaker_id)
    if db_speaker is None:
        raise HTTPException(status_code=404, detail="Speaker not found")
    return db_speaker

@router.put("/speakers", response_model=schemas.Speaker)
def update_speaker(speaker: schemas.SpeakerUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    if all(value is None for value in dict(speaker).values()):
        raise HTTPException(status_code=400, detail="Invalid request body")
    db_speaker = crud.get_speaker(db, speaker_id=speaker.id)
    if db_speaker is None:
        raise HTTPException(status_code=404, detail="Speaker not found")
    if speaker.conference_id is not None:
        if conferences_crud.get_conference_by_uuid(db=db,uuid=speaker.conference_id,owner_id=current_user.id) is None:
            raise HTTPException(status_code=404, detail="Conference not found")
    return crud.update_speaker(db=db, speaker=speaker)

@router.delete("/speakers/{speaker_id}")
def delete_speaker(speaker_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_speaker = crud.get_speaker(db, speaker_id=speaker_id)
    if db_speaker is None:
        raise HTTPException(status_code=404, detail="Speaker not found")
    return crud.delete_speaker(db=db, speaker_id=speaker_id)