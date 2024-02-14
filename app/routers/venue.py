from ..dependencies import get_db
from ..crud import venue_crud as crud
from ..crud import users_crud
from ..schemas import venue_schemas as schemas
from ..schemas.user_schemas import UserAuthentication as User
from fastapi import APIRouter, Security, HTTPException, status, Depends
from sqlalchemy.orm import Session
from ..oauth2 import get_current_active_user
import logging

router = APIRouter(tags=['venues'])

@router.get("/venues/get-all-venues", response_model=list[schemas.Venue])
def get_all_venues(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    venues = crud.get_all_venues(db, offset, limit)
    if not venues or len(venues) == 0:
        logging.exception("No venues found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No venues found")
    logging.info(f"Venues retrieved successfully")
    return venues

@router.get("/venues", response_model=list[schemas.Venue])
def get_all_venues_by_owner_id(offset: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_user = users_crud.get_user(db, current_user.id)
    if not db_user:
        logging.exception(f"User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    venues = crud.get_all_venues_by_owner_id(db, current_user.id, offset, limit)
    if not venues or len(venues) == 0:
        logging.exception(f"No venues found for user {db_user.uuid}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No venues found for user {db_user.uuid}")
    logging.info(f"Venues retrieved successfully for user: {db_user.uuid}")
    return venues

@router.get("/venues/{venue_id}", response_model=schemas.Venue)
def get_venue_by_id(venue_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_venue = crud.get_venue_by_id(db, venue_id, current_user.id)
    if not db_venue:
        logging.exception(f"Venue not found: {venue_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue not found: {venue_id}")
    logging.info(f"Venue retrieved successfully: {venue_id}")
    return db_venue

@router.post("/venues", response_model=schemas.Venue, status_code=status.HTTP_201_CREATED)
def create_venue(venue: schemas.VenueCreate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_venue = crud.create_venue(db, venue, current_user.id)
    logging.info(f"Venue created successfully: {db_venue.uuid}")
    return db_venue

@router.put("/venues", response_model=schemas.Venue)
def update_venue(venue: schemas.VenueUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_venue = crud.get_venue_by_id(db, venue.id, current_user.id)
    if not db_venue:
        logging.exception(f"Venue not found: {venue.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue not found: {venue.id}")
    db_venue = crud.update_venue(db, venue, db_venue)
    logging.info(f"Venue updated successfully: {venue.id}")
    return db_venue

@router.delete("/venues/{venue_id}")
def delete_venue(venue_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_venue = crud.get_venue_by_id(db, venue_id, current_user.id)
    if not db_venue:
        logging.exception(f"Venue not found: {venue_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue not found")
    db_venue = crud.delete_venue(db, db_venue)
    logging.info(f"Venue deleted successfully: {venue_id}")
    return db_venue