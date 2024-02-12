from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..basicauth import basic_auth
from ..schemas.static_table_schemas import StaticSession, StaticTableOutput
import uuid
import logging
from datetime import datetime
from .. import models
from ..static_enums import session

router = APIRouter(tags=["session_status"])

@router.post("/session_status", response_model=StaticTableOutput, status_code=status.HTTP_201_CREATED)
def create_session_status(static_session: StaticSession, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    session_dict = static_session.model_dump()
    session_dict["status"] = session_dict["status"].lower()
    db_static_session = models.Sessionstatus(**session_dict)
    db_static_session.id = session.SessionEnum[db_static_session.status.upper()].value
    db_static_session.created_on = db_static_session.updated_on = datetime.utcnow()
    db_static_session.uuid = str(uuid.uuid4())
    db.add(db_static_session)
    try:
        db.commit()
    except:
        db.rollback()
        logging.exception("Status already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status already exists")
    db.refresh(db_static_session)
    db_static_session.status = db_static_session.status.upper()
    logging.info(f"Status created with id {db_static_session.uuid}")
    return db_static_session

@router.get("/session_status", response_model=list[StaticTableOutput])
def get_session_status(db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    static_session = db.query(models.Sessionstatus).all()
    if static_session is None or len(static_session) == 0:
        logging.exception("no status found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no status found")
    logging.info("session status retrieved")
    return static_session

@router.delete("/session_status/{status_id}", response_model=StaticTableOutput)
def delete_session_status(status_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    static_session = db.query(models.Sessionstatus).filter(models.Sessionstatus.uuid == status_id).first()
    if static_session is None:
        logging.exception("status not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="status not found")
    db.delete(static_session)
    db.commit()
    logging.info(f"status deleted with id {static_session.uuid}")
    return True