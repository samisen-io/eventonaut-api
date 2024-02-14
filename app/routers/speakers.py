import logging
import random
from ..dependencies import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Security, status
from ..schemas import speaker_schemas as schemas
from ..crud import speakers_crud as crud, conferences_crud
from app.oauth2 import get_current_active_user
from app.schemas.user_schemas import UserAuthentication as User
from email_validator import validate_email, EmailNotValidError

router = APIRouter(tags=["speakers"])

@router.post("/speakers", response_model=schemas.Speaker, status_code=status.HTTP_201_CREATED)
def create_speaker(speaker: schemas.SpeakerCreate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    try:
        valid = validate_email(speaker.email)
        speaker.email = valid.normalized.lower()
    except EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if crud.get_speaker_by_email(db=db, email=speaker.email, owner_id=current_user.id) is not None:
        logging.exception("Email already registered")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    speaker = crud.create_speaker(db=db, speaker=speaker, owner_id=current_user.id)
    logging.info("Speaker created: " + speaker.uuid)
    return speaker

@router.get("/speakers/get-all-speakers", response_model=list[schemas.Speaker])
def get_all_speakers(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    speakers = crud.get_all_speakers(db, offset=offset, limit=limit)
    if speakers is None or len(speakers) == 0:
        logging.exception("Speaker not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speaker not found")
    logging.info("All speakers got retrieved")
    return speakers

@router.get("/speakers/conference/{conference_id}", response_model=list[schemas.Speaker])
def get_speakers_by_conference_id(conference_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    speakers = crud.get_speakers_by_conference_id_owner_id(db=db, conference_id=conference_id, owner_id=current_user.id)
    if speakers is None or len(speakers) == 0:
        logging.exception("Speaker not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speaker not found")
    logging.info("Speakers retrieved for conference: " + conference_id)
    return speakers

@router.get("/speakers", response_model=list[schemas.Speaker])
def get_speakers_by_owner_id(offset: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    speakers = crud.get_speakers_by_owner_id(db=db, owner_id=current_user.id, offset=offset, limit=limit)
    if speakers is None or len(speakers) == 0:
        logging.exception("Speaker not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speaker not found")
    logging.info("Speakers retrieved for owner: " + str(current_user.id))
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