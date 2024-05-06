from app.static_enums.role import RoleEnum
from ..dependencies import get_db
from ..crud import venue_crud as crud
from ..crud import users_crud
from ..schemas import venue_schemas as schemas
from ..schemas.user_schemas import UserAuthentication as User
from fastapi import APIRouter, Security, HTTPException, status, Depends
from sqlalchemy.orm import Session
from ..oauth2 import get_current_active_user, get_current_active_organization
import logging
from ..schemas.organization_schemas import OrganizationSecurity

router = APIRouter(tags=['venues'])

@router.get("/venues/get-all-venues", response_model=list[schemas.VenueResponse], include_in_schema=False)
def get_all_venues(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    venues = crud.get_all_venues(db, offset, limit)
    if not venues or len(venues) == 0:
        logging.exception("No venues found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No venues found")
    logging.info(f"Venues retrieved successfully")
    return venues

@router.get("/venues", response_model=list[schemas.VenueResponse])
def get_all_venues_by_organization_id(offset: int = 0, limit: int = 100, db: Session = Depends(get_db), current_organization:  OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    venues = crud.get_all_venues_by_organization_id(db,current_organization.id, offset, limit)
    if not venues or len(venues) == 0:
        logging.exception(f"No venues found for Organization {current_organization.uuid}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No venues found for user {current_organization.uuid}")
    logging.info(f"Venues retrieved successfully for user: {current_organization.uuid}")
    return venues

@router.get("/venues/{venue_id}", response_model=schemas.VenueResponse)
def get_venue_by_id(venue_id: str, db: Session = Depends(get_db), current_organization:  OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    db_venue = crud.get_venue_by_id_for_organization(db, venue_id, current_organization.id)
    if not db_venue:
        logging.exception(f"Venue not found: {venue_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue not found: {venue_id}")
    logging.info(f"Venue retrieved successfully: {venue_id}")
    return db_venue

@router.post("/venues", response_model=schemas.VenueResponse, status_code=status.HTTP_201_CREATED)
def create_venue(venue: schemas.VenueCreate, db: Session = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    db_venue = crud.create_venue(db, venue, current_organization.id)
    logging.info(f"Venue created successfully: {db_venue.uuid}")
    return db_venue

@router.put("/venues", response_model=schemas.VenueResponse)
def update_venue(venue: schemas.VenueUpdate, db: Session = Depends(get_db), current_organization:  OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    db_venue = crud.get_venue_by_id_for_organization(db, venue.id, current_organization.id)
    if not db_venue:
        logging.exception(f"Venue not found: {venue.id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue not found: {venue.id}")
    db_venue = crud.update_venue(db, venue, db_venue)
    logging.info(f"Venue updated successfully: {venue.id}")
    return db_venue

@router.delete("/venues/{venue_id}")
def delete_venue(venue_id: str, db: Session = Depends(get_db), current_organization:  OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    db_venue = crud.get_venue_by_id_for_organization(db, venue_id, current_organization.id)
    if not db_venue:
        logging.exception(f"Venue not found: {venue_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Venue not found")
    db_venue = crud.delete_venue(db, db_venue)
    logging.info(f"Venue deleted successfully: {venue_id}")
    return db_venue