from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..basicauth import basic_auth
from ..schemas.static_table_schemas import StaticEvent, StaticTableOutput
import uuid
import logging
from datetime import datetime
from .. import models
from ..static_enums import event

router = APIRouter(tags=["static_event"])

@router.post("/static_event", response_model=StaticTableOutput, status_code=status.HTTP_201_CREATED)
def create_static_event(static_event: StaticEvent, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    event_dict = static_event.model_dump()
    event_dict["status"] = event_dict["status"].lower()
    db_static_event = models.StaticEvent(**event_dict)
    db_static_event.id = event.EventEnum[db_static_event.status.upper()].value
    db_static_event.created_on = db_static_event.updated_on = datetime.utcnow()
    db_static_event.uuid = str(uuid.uuid4())
    db.add(db_static_event)
    try:
        db.commit()
    except:
        db.rollback()
        logging.exception("Status already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status already exists")
    db.refresh(db_static_event)
    db_static_event.status = db_static_event.status.upper()
    logging.info(f"Status created with id {db_static_event.uuid}")
    return db_static_event

@router.get("/static_event", response_model=list[StaticTableOutput])
def get_static_event(db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    static_event = db.query(models.StaticEvent).all()
    if static_event is None or len(static_event) == 0:
        logging.exception("no status found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no status found")
    logging.info("event status retrieved")
    return static_event

@router.delete("/static_event/{status_id}", response_model=StaticTableOutput)
def delete_static_event(status_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    static_event = db.query(models.StaticEvent).filter(models.StaticEvent.uuid == status_id).first()
    if static_event is None:
        logging.exception("status not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="status not found")
    db.delete(static_event)
    db.commit()
    logging.info(f"status deleted with id {static_event.uuid}")
    return static_event