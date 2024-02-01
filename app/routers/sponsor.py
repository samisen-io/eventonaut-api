from ..schemas import sponsor_schemas as schemas
from ..crud import sponsors_crud
from fastapi import HTTPException, status, Depends, APIRouter, Security
from sqlalchemy.orm import Session
import logging
from ..dependencies import get_db
import email_validator
from ..oauth2 import get_current_active_user
from ..crud import conferences_crud

router = APIRouter(tags=["sponsors"])

@router.post("/sponsors", status_code=status.HTTP_201_CREATED, response_model=schemas.Sponsor)
def create_sponsor(sponsor: schemas.SponsorCreate, db: Session = Depends(get_db), current_user = Security(get_current_active_user, scopes=["organizer"])):
    try:
        valid = email_validator.validate_email(sponsor.email)
        sponsor.email = valid.normalized.lower()
    except email_validator.EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if sponsors_crud.get_sponsor_by_email(db, sponsor.email, current_user.id):
        logging.exception("Email already exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    sponsor = sponsors_crud.create_sponsor(db, sponsor, current_user.id)
    logging.info(f"Sponsor created with id {sponsor.uuid}")
    return sponsor

@router.get("/sponsors", response_model=list[schemas.Sponsor])
def get_all_sponsors(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    sponsors = sponsors_crud.get_all_sponsors(db=db, limit=limit, offset=offset)
    if sponsors is None or len(sponsors) == 0:
        logging.exception("Sponsors not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsors not found")
    logging.info("Sponsors retrieved")
    return sponsors

@router.get("/sponsors/{sponsor_id}", response_model=schemas.Sponsor)
def get_sponsor_by_id(sponsor_id: str, db: Session = Depends(get_db), current_user = Security(get_current_active_user, scopes=["organizer"])):
    sponsor = sponsors_crud.get_sponsor_by_uuid(db=db, uuid=sponsor_id, owner_id=current_user.id)
    if sponsor is None:
        logging.exception("Sponsor not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsor not found")
    logging.info(f"Sponsor retrieved with id {sponsor.uuid}")
    return sponsor

  #Need to change the code fit with new event sponsors table
@router.get("/sponsors/{conference_id}", response_model=list[schemas.Sponsor])
def get_sponsors_by_conference_id(conference_id: str, db: Session = Depends(get_db), current_user = Security(get_current_active_user, scopes=["organizer"])):
    conference = conferences_crud.get_conference_by_uuid(db=db, uuid=conference_id, owner_id=current_user.id)
    if conference is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    sponsors = sponsors_crud.get_sponsors_by_conference_id(db=db, conference_id=conference.id)
    if sponsors is None or len(sponsors) == 0:
        logging.exception("Sponsors not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsors not found")
    logging.info(f"Sponsors retrieved for conference id {conference_id}")
    return sponsors

@router.put("/sponsors", response_model=schemas.Sponsor)
def update_sponsor(sponsor: schemas.SponsorUpdate, db: Session = Depends(get_db), current_user = Security(get_current_active_user, scopes=["organizer"])):
    sponsor_dict = sponsor.model_dump()
    sponsor_dict.pop('id')
    if all(value is None for value in sponsor_dict.values()):
        logging.exception("Invalid Request Body")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Request Body")
    db_sponsor = sponsors_crud.get_sponsor_by_uuid(db=db, uuid=sponsor.id, owner_id=current_user.id)
    if db_sponsor is None:
        logging.exception("Sponsor not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsor not found")
    sponsor = sponsors_crud.update_sponsor(db=db, sponsor=sponsor, db_sponsor=db_sponsor)
    logging.info(f"Sponsor updated with id {sponsor.uuid}")
    return sponsor

@router.delete("/sponsors/{sponsor_id}")
def delete_sponsor(sponsor_id: str, db: Session = Depends(get_db), current_user = Security(get_current_active_user, scopes=["organizer"])):
    sponsor = sponsors_crud.get_sponsor_by_uuid(db=db, uuid=sponsor_id, owner_id=current_user.id)
    if sponsor is None:
        logging.exception("Sponsor not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsor not found")
    deleted_sponsor = sponsors_crud.delete_sponsor(db=db, db_sponsor=sponsor)
    logging.info(f"Sponsor deleted with id {sponsor.uuid}")
    return deleted_sponsor