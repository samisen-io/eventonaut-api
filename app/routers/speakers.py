import logging
from ..dependencies import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Security, status
from ..schemas import speaker_schemas as schemas
from ..crud import speakers_crud as crud, conferences_crud
from app.oauth2 import get_current_active_user
from app.schemas.user_schemas import UserAuthentication as User


router = APIRouter(tags=["speakers"])

@router.post("/speakers", response_model=schemas.Speaker, status_code=status.HTTP_201_CREATED)
def create_speaker(speaker: schemas.SpeakerCreate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    if conferences_crud.get_conference_by_uuid(db=db,uuid=speaker.conference_id,owner_id=current_user.id) is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    speaker = crud.create_speaker(db=db, speaker=speaker)
    logging.info("Speaker created: " + speaker.uuid)
    return speaker

@router.get("/speakers", response_model=list[schemas.Speaker])
def get_all_speakers(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    speakers = crud.get_all_speakers(db, offset=offset, limit=limit)
    if speakers is None or len(speakers) == 0:
        logging.exception("Speaker not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speaker not found")
    logging.info("All speakers got retrieved")
    return speakers

@router.get("/speakers/{speaker_id}", response_model=schemas.Speaker)
def get_speaker(speaker_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_speaker = crud.get_speaker(db, speaker_id=speaker_id)
    if db_speaker is None:
        logging.exception("Speaker not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speaker not found")
    logging.info("Speaker retrieved: " + speaker_id)
    return db_speaker

@router.put("/speakers", response_model=schemas.Speaker)
def update_speaker(speaker: schemas.SpeakerUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    if all(value is None for value in dict(speaker).values()):
        logging.exception("Invalid request body")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")
    db_speaker = crud.get_speaker(db, speaker_id=speaker.id)
    if db_speaker is None:
        logging.exception("Speaker not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speaker not found")
    if speaker.conference_id is not None:
        if conferences_crud.get_conference_by_uuid(db=db,uuid=speaker.conference_id,owner_id=current_user.id) is None:
            logging.exception("Conference not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    updated_speaker = crud.update_speaker(db=db, speaker=speaker)
    logging.info("Speaker updated: " + updated_speaker.uuid)
    return updated_speaker

@router.delete("/speakers/{speaker_id}")
def delete_speaker(speaker_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_speaker = crud.get_speaker(db, speaker_id=speaker_id)
    if db_speaker is None:
        logging.exception("Speaker not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speaker not found")
    deleted_speaker = crud.delete_speaker(db=db, speaker_id=speaker_id)
    logging.info("Speaker deleted: " + speaker_id)
    return deleted_speaker