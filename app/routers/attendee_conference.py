from fastapi import APIRouter, HTTPException, Depends, Security, status
import logging
from app.oauth2 import get_current_active_user
from ..dependencies import get_db
from sqlalchemy.orm import Session
from ..schemas import attendee_schemas as schemas, attendee_conference_schemas, conference_schemas
from ..crud import attendee_crud as crud, conferences_crud
from app.schemas.user_schemas import UserAuthentication as User

router = APIRouter(tags=["attendee conference"])

@router.post("/attendee/conference", response_model=attendee_conference_schemas.AttendeeConference, status_code=status.HTTP_201_CREATED)
def create_attendee_conference(attendee_conference: attendee_conference_schemas.AttendeeConferenceCreate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    attendee = crud.get_attendee_by_id(db, attendee_id=current_user.id)
    if not attendee:
        logging.exception("Attendee not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendee not found")
    conference = conferences_crud.get_conference_by_code(db=db, code=attendee_conference.conference_code)
    if not conference:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    if crud.get_attendee_conference_by_attendee_id_and_conference_id(db=db, attendee_id=current_user.id, conference_id=conference.uuid):
        logging.exception("Conference already exists")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conference already exists")
    attendee_conf = crud.create_attendee_conference(db=db, attendee_conference=attendee_conference, attendee_id=current_user.id)
    logging.info(f"Conference-{conference.uuid} added to attendee-{attendee_conf.uuid}")
    return attendee_conf

@router.post("/attendee/conference-id", response_model=attendee_conference_schemas.AttendeeConference, status_code=status.HTTP_201_CREATED)
def create_attendee_conference_by_id(attendee_conference: attendee_conference_schemas.AttendeeConferenceCreateId, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    attendee = crud.get_attendee_by_id(db, attendee_id=current_user.id)
    if not attendee:
        logging.exception("Attendee not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendee not found")
    conference = conferences_crud.get_conf_by_uuid(db=db, conference_id=attendee_conference.conference_id)
    if not conference:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    if crud.get_attendee_conference_by_attendee_id_and_conference_id(db=db, attendee_id=current_user.id, conference_id=conference.uuid):
        logging.exception("Conference already exixts")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Conference already exists")
    attendee_conf = crud.create_attendee_conference(db=db, attendee_conference=attendee_conference, attendee_id=current_user.id)
    logging.info(f"Conference-{conference.uuid} added to attendee-{attendee_conf.uuid}")
    return attendee_conf

# get all attendee conferences
@router.get("/attendee/conference", response_model=list[conference_schemas.Conference])
def get_all_attendee_conferences(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    if not crud.get_attendee_by_id(db, attendee_id=current_user.id):
        logging.exception("Attendee not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendee not found")
    attendee_conferences = crud.get_all_attendee_conferences(db, skip=skip, limit=limit, attendee_id=current_user.id)
    if not attendee_conferences or len(attendee_conferences) == 0:
        logging.exception("No conferences found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No conferences found")
    logging.info("All conferences for attendee retrieved")
    return attendee_conferences

# delete attendee conference by attendee id and conference id
@router.delete("/attendee/conference/{conference_code}")
def delete_attendee_conference_by_attendee_id_and_conference_id(conference_code: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    attendee = crud.get_attendee_by_id(db, attendee_id=current_user.id)
    if not attendee:
        logging.exception("Attendee not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendee not found")
    conference = conferences_crud.get_conference_by_code(db=db, code = conference_code)
    if not conference:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    if not crud.get_attendee_conference_by_attendee_id_and_conference_id(db=db, attendee_id=current_user.id, conference_id=conference.uuid):
        logging.exception("No conference found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No conference found")
    deleted_attendee_conference = crud.delete_attendee_conference_by_attendee_id_and_conference_id(db=db, attendee_id=current_user.id, conference_code=conference_code)
    logging.info(f"Conference-{conference.uuid} deleted for attendee-{attendee.uuid}")
    return deleted_attendee_conference

@router.get("/attendee/profiles", response_model=list[schemas.Attendee])
def get_attendee_profiles_for_session_id(conference_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    if not conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id):
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    attendees = crud.get_all_attendee_profiles_by_conference_id(db=db, conference_id=conference_id)
    if not attendees or len(attendees) == 0:
        logging.exception("No attendees found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No attendees found")
    logging.info("All attendee profiles retrieved")
    return attendees