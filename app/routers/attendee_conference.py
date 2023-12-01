from fastapi import APIRouter, HTTPException, Depends, Security

from app.oauth2 import get_current_active_user
from ..dependencies import get_db
from sqlalchemy.orm import Session
from ..schemas import attendee_schemas as schemas, attendee_conference_schemas, conference_schemas
from ..crud import attendee_crud as crud, conferences_crud
from app.schemas.user_schemas import UserAuthentication as User

router = APIRouter(tags=["attendee conference"])

@router.post("/attendee/conference")
def create_attendee_conference(attendee_conference: attendee_conference_schemas.AttendeeConferenceCreate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    if not crud.get_attendee_by_id(db, attendee_id=current_user.id):
        raise HTTPException(status_code=400, detail="Attendee not found")
    conference = conferences_crud.get_conference_by_code(db=db, code=attendee_conference.conference_code)
    if not conference:
        raise HTTPException(status_code=400, detail="Conference not found")
    if crud.get_attendee_conference_by_attendee_id_and_conference_id(db=db, attendee_id=current_user.id, conference_id=conference.uuid):
        raise HTTPException(status_code=400, detail="Conference already exists")
    return crud.create_attendee_conference(db=db, attendee_conference=attendee_conference, attendee_id=current_user.id)

# get all attendee conferences
@router.get("/attendee/conference", response_model=list[conference_schemas.Conference])
def get_all_attendee_conferences(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    if not crud.get_attendee_by_id(db, attendee_id=current_user.id):
        raise HTTPException(status_code=400, detail="Attendee not found")
    attendee_conferences = crud.get_all_attendee_conferences(db, skip=skip, limit=limit, attendee_id=current_user.id)
    if not attendee_conferences or len(attendee_conferences) == 0:
        raise HTTPException(status_code=404, detail="No conferences found")
    return attendee_conferences

# delete attendee conference by attendee id and conference id
@router.delete("/attendee/conference/{conference_code}")
def delete_attendee_conference_by_attendee_id_and_conference_id(conference_code: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    if not crud.get_attendee_by_id(db, attendee_id=current_user.id):
        raise HTTPException(status_code=400, detail="Attendee not found")
    conference = conferences_crud.get_conference_by_code(db=db, code = conference_code)
    if not conference:
        raise HTTPException(status_code=400, detail="Conference not found")
    if not crud.get_attendee_conference_by_attendee_id_and_conference_id(db=db, attendee_id=current_user.id, conference_id=conference.uuid):
        raise HTTPException(status_code=404, detail="No conference found")
    return crud.delete_attendee_conference_by_attendee_id_and_conference_id(db=db, attendee_id=current_user.id, conference_code=conference_code)

@router.get("/attendee/profiles/", response_model=list[schemas.Attendee])
def get_attendee_profiles_for_session_id(conference_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    if not conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id):
        raise HTTPException(status_code=400, detail="Conference not found")
    return crud.get_all_attendee_profiles_by_conference_id(db=db, conference_id=conference_id)