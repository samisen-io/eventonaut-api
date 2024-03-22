from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..basicauth import basic_auth
from ..schemas.static_table_schemas import StaticOrganizer, StaticTableOutput
import uuid
import logging
from datetime import datetime
from .. import models
from ..static_enums import organizer

router = APIRouter(tags=["static_organizer"])

@router.post("/static_organizer", response_model=StaticTableOutput, status_code=status.HTTP_201_CREATED)
def create_static_organizer(static_organizer: StaticOrganizer, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    organizer_dict = static_organizer.model_dump()
    organizer_dict["status"] = organizer_dict["status"].lower()
    db_static_organizer = models.OrganizerStatus(**organizer_dict)
    db_static_organizer.id = organizer.OrganizerEnum[db_static_organizer.status.upper()].value
    db_static_organizer.created_on = db_static_organizer.updated_on = datetime.utcnow()
    db_static_organizer.uuid = str(uuid.uuid4())
    db.add(db_static_organizer)
    try:
        db.commit()
    except:
        db.rollback()
        logging.exception("Status already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status already exists")
    db.refresh(db_static_organizer)
    db_static_organizer.status = db_static_organizer.status.upper()
    logging.info(f"Status created with id {db_static_organizer.uuid}")
    return db_static_organizer

@router.get("/static_organizer", response_model=list[StaticTableOutput])
def get_static_organizer(db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    static_organizer = db.query(models.OrganizerStatus).order_by(models.OrganizerStatus.updated_on.desc()).all()
    if static_organizer is None or len(static_organizer) == 0:
        logging.exception("no status found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no status found")
    logging.info("organizer status retrieved")
    return static_organizer

@router.delete("/static_organizer/{status_id}", response_model=StaticTableOutput)
def delete_static_organizer(status_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    static_organizer = db.query(models.OrganizerStatus).filter(models.OrganizerStatus.uuid == status_id).first()
    if static_organizer is None:
        logging.exception("status not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="status not found")
    db.delete(static_organizer)
    db.commit()
    logging.info(f"status deleted with id {static_organizer.uuid}")
    return True