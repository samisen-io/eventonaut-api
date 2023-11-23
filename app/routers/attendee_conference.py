# create attendee conference
from fastapi import APIRouter, HTTPException, Depends
from ..dependencies import get_db
from sqlalchemy.orm import Session
from ..schemas import attendee_schemas as schemas, attendee_conference_schemas, conference_schemas
from ..crud import attendee_crud as crud, conferences_crud

router = APIRouter(tags=["attendee conference"])

@router.post("/attendee/conference", response_model=attendee_conference_schemas.AttendeeConference)
def create_attendee_conference(attendee_conference: attendee_conference_schemas.AttendeeConferenceCreate, db: Session = Depends(get_db)):
    if not crud.get_attendee_by_uuid(db, attendee_id=attendee_conference.attendee_id):
        raise HTTPException(status_code=400, detail="Attendee not found")
    conference = conferences_crud.get_conference_by_code(db=db, code=attendee_conference.conference_code)
    if not conference:
        raise HTTPException(status_code=400, detail="Conference not found")
    if crud.get_attendee_conference_by_attendee_id_and_conference_id(db=db, attendee_id=attendee_conference.attendee_id, conference_id=conference.uuid):
        raise HTTPException(status_code=400, detail="Conference already exists")
    return crud.create_attendee_conference(db=db, attendee_conference=attendee_conference)

# get all attendee conferences
@router.get("/attendee/conference/{attendee_id}", response_model=list[conference_schemas.Conference])
def get_all_attendee_conferences(attendee_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if not crud.get_attendee_by_uuid(db, attendee_id=attendee_id):
        raise HTTPException(status_code=400, detail="Attendee not found")
    attendee_conferences = crud.get_all_attendee_conferences(db, skip=skip, limit=limit, attendee_id=attendee_id)
    if not attendee_conferences or len(attendee_conferences) == 0:
        raise HTTPException(status_code=404, detail="No conferences found")
    return attendee_conferences

# delete attendee conference by attendee id and conference id
@router.delete("/attendee/conference/{attendee_id}/{conference_code}")
def delete_attendee_conference_by_attendee_id_and_conference_id(attendee_id: str, conference_code: str, db: Session = Depends(get_db)):
    if not crud.get_attendee_by_uuid(db, attendee_id=attendee_id):
        raise HTTPException(status_code=400, detail="Attendee not found")
    conference = conferences_crud.get_conference_by_code(db=db, code = conference_code)
    if not conference:
        raise HTTPException(status_code=400, detail="Conference not found")
    if not crud.get_attendee_conference_by_attendee_id_and_conference_id(db=db, attendee_id=attendee_id, conference_id=conference.uuid):
        raise HTTPException(status_code=404, detail="No conference found")
    return crud.delete_attendee_conference_by_attendee_id_and_conference_id(db=db, attendee_id=attendee_id, conference_code=conference_code)

@router.get("/attendee/profiles/", response_model=list[schemas.Attendee])
def get_attendee_profiles_for_session_id(conference_id: str, db: Session = Depends(get_db)):
    if not conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id):
        raise HTTPException(status_code=400, detail="Conference not found")
    return crud.get_all_attendee_profiles_by_conference_id(db=db, conference_id=conference_id)