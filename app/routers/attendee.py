from fastapi import APIRouter, HTTPException, Depends
from ..dependencies import get_db
from sqlalchemy.orm import Session
from ..schemas import attendee_schemas as schemas, attendee_conference_schemas, conference_schemas
from ..crud import attendee_crud as crud, conferences_crud, sessions_crud
from email_validator import validate_email, EmailNotValidError

router = APIRouter(tags=["attendee"])

# create attendee
@router.post("/attendee/signup", response_model=schemas.Attendee)
def create_attendee(attendee: schemas.AttendeeCreate, db: Session = Depends(get_db)):
    try:
        valid = validate_email(attendee.email)
        attendee.email = valid.normalized.lower()
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db_attendee = crud.get_attendee_by_email(db, email=attendee.email)
    if db_attendee:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_attendee(db=db, attendee=attendee)

# get all attendees
@router.get("/attendee", response_model=list[schemas.Attendee])
def get_all_attendees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    attendees = crud.get_attendees(db, skip=skip, limit=limit)
    if not attendees or len(attendees) == 0:
        raise HTTPException(status_code=404, detail="No attendees found")
    return attendees

# get attendee by id
@router.get("/attendee/{attendee_id}", response_model=schemas.Attendee)
def get_attendee_by_id(attendee_id: str, db: Session = Depends(get_db)):
    db_attendee = crud.get_attendee_by_uuid(db, attendee_id=attendee_id)
    if not db_attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return db_attendee

@router.get("/attendee/profiles/", response_model=list[schemas.Attendee])
def get_attendee_profiles_for_session_id(conference_id: str, db: Session = Depends(get_db)):
    if not conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id):
        raise HTTPException(status_code=400, detail="Conference not found")
    return crud.get_all_attendee_profiles_by_conference_id(db=db, conference_id=conference_id)

# update attendee by email
@router.put("/attendee", response_model=schemas.Attendee)
def update_attendee_by_id(attendee: schemas.AttendeeUpdate, db: Session = Depends(get_db)):
    if attendee.first_name is None and attendee.last_name is None:
        raise HTTPException(status_code=400, detail="Invalid request body")
    if not crud.get_attendee_by_uuid(db, attendee_id=attendee.id):
        raise HTTPException(status_code=400, detail="Attendee not found")
    return crud.update_attendee_by_uuid(db=db, attendee_id=attendee.id, attendee=attendee)

# update attende password by id
@router.put("/attendee/password", response_model=schemas.Attendee)
def update_attendee_password_by_id(attendee: schemas.AttendePassword, db: Session = Depends(get_db)):
    if not crud.get_attendee_by_uuid(db, attendee_id=attendee.id):
        raise HTTPException(status_code=400, detail="Attendee not found")
    return crud.update_attendee_password_by_uuid(db=db, attendee_id=attendee.id, attendee=attendee)

# delete all attendee by id
@router.delete("/attendee/{attendee_id}")
def delete_attendee_by_id(attendee_id: str, db: Session = Depends(get_db)):
    db_attendee = crud.get_attendee_by_uuid(db, attendee_id=attendee_id)
    if not db_attendee:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return crud.delete_attendee_by_uuid(db, attendee_id=attendee_id)

# create attendee conference
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
@router.get("/attendee/conference/{attendee_id}")
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