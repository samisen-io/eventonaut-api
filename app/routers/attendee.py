from fastapi import APIRouter, HTTPException, Depends, Security, status
import logging
from app.oauth2 import get_current_active_user
from ..dependencies import get_db
from sqlalchemy.orm import Session
from ..schemas import attendee_schemas as schemas
from ..crud import attendee_crud as crud
from email_validator import validate_email, EmailNotValidError
from app.schemas.user_schemas import UserAuthentication as User
from .. import basicauth

router = APIRouter(tags=["attendee"])

# create attendee
@router.post("/attendee/signup", response_model=schemas.Attendee, status_code=status.HTTP_201_CREATED)
def create_attendee(attendee: schemas.AttendeeCreate, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    try:
        valid = validate_email(attendee.email)
        attendee.email = valid.normalized.lower()
    except EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    db_attendee = crud.get_attendee_by_email(db, email=attendee.email)
    if db_attendee:
        logging.exception("Email already registered")
        raise HTTPException(status_code=400, detail="Email already registered")
    attendee = crud.create_attendee(db=db, attendee=attendee)
    logging.info("Attendee created: " + db_attendee.uuid)
    return attendee

# get all attendees
@router.get("/attendee/all-attendees", response_model=list[schemas.Attendee])
def get_all_attendees(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    attendees = crud.get_attendees(db, skip=skip, limit=limit)
    if not attendees or len(attendees) == 0:
        logging.exception("No attendees found")
        raise HTTPException(status_code=404, detail="No attendees found")
    logging.info("All attendees retrieved")
    return attendees

# get attendee by id
@router.get("/attendee", response_model=schemas.Attendee)
def get_attendee_by_id(db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    db_attendee = crud.get_attendee_by_id(db, attendee_id=current_user.id)
    if not db_attendee:
        logging.exception("Attendee not found")
        raise HTTPException(status_code=404, detail="Attendee not found")
    logging.info("Attendee retrieved: " + db_attendee.email)
    return db_attendee

# update attendee by email
@router.put("/attendee", response_model=schemas.Attendee)
def update_attendee_by_id(attendee: schemas.AttendeeUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    if all(value is None for value in dict(attendee).values()):
        logging.exception("Invalid request body")
        raise HTTPException(status_code=400, detail="Invalid request body")
    if not crud.get_attendee_by_id(db, attendee_id=current_user.id):
        logging.exception("Attendee not found")
        raise HTTPException(status_code=400, detail="Attendee not found")
    updated_attendee = crud.update_attendee_by_uuid(db=db, attendee_id=current_user.id, attendee=attendee)
    logging.info("Attendee updated: " + updated_attendee.uuid)
    return updated_attendee

# update attende password by id
@router.put("/attendee/password", response_model=schemas.Attendee)
def update_attendee_password_by_id(attendee: schemas.AttendePassword, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    if not crud.get_attendee_by_id(db, attendee_id=current_user.id):
        logging.exception("Attendee not found")
        raise HTTPException(status_code=400, detail="Attendee not found")
    if attendee.old_password == attendee.new_password:
        logging.exception("New password cannot be same as old password")
        raise HTTPException(status_code=400, detail="New password cannot be same as old password")
    updated_attendee = crud.update_attendee_password_by_uuid(db=db, attendee_id=current_user.id, attendee=attendee)
    if not updated_attendee:
        logging.exception("Invalid old password")
        raise HTTPException(status_code=400, detail="Invalid old password")
    logging.info("Attendee password updated: " + updated_attendee.uuid)
    return updated_attendee

# delete all attendee by id
@router.delete("/attendee")
def delete_attendee_by_id(db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    db_attendee = crud.get_attendee_by_id(db, attendee_id=current_user.id)
    if not db_attendee:
        logging.exception("Attendee not found")
        raise HTTPException(status_code=404, detail="Attendee not found")
    deleted_attendee = crud.delete_attendee_by_uuid(db, attendee_id=current_user.id)
    logging.info("Attendee deleted: " + db_attendee.uuid)
    return deleted_attendee

