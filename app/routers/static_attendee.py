from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..basicauth import basic_auth
from ..schemas.static_table_schemas import StaticAttendee, StaticTableOutput
import uuid
import logging
from datetime import datetime
from .. import models
from ..static_enums import attendee

router = APIRouter(tags=["attendee_status"])

@router.post("/attendee_status", response_model=StaticTableOutput, status_code=status.HTTP_201_CREATED)
def create_attendee_status(static_attendee: StaticAttendee, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    attendee_dict = static_attendee.model_dump()
    attendee_dict["status"] = attendee_dict["status"].lower()
    db_static_attendee = models.AttendeeStatus(**attendee_dict)
    db_static_attendee.id = attendee.AttendeeEnum[db_static_attendee.status.upper()].value
    db_static_attendee.created_on = db_static_attendee.updated_on = datetime.utcnow()
    db_static_attendee.uuid = str(uuid.uuid4())
    db.add(db_static_attendee)
    try:
        db.commit()
    except:
        db.rollback()
        logging.exception("Status already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status already exists")
    db.refresh(db_static_attendee)
    db_static_attendee.status = db_static_attendee.status.upper()
    logging.info(f"Status created with id {db_static_attendee.uuid}")
    return db_static_attendee

@router.get("/attendee_status", response_model=list[StaticTableOutput])
def get_attendee_status(db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    static_attendee = db.query(models.AttendeeStatus).all()
    if static_attendee is None or len(static_attendee) == 0:
        logging.exception("no status found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no status found")
    logging.info("attendee status retrieved")
    return static_attendee

@router.delete("/attendee_status/{status_id}", response_model=StaticTableOutput)
def delete_attendee_status(status_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    static_attendee = db.query(models.AttendeeStatus).filter(models.AttendeeStatus.uuid == status_id).first()
    if static_attendee is None:
        logging.exception("status not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="status not found")
    db.delete(static_attendee)
    db.commit()
    logging.info(f"status deleted with id {static_attendee.uuid}")
    return True