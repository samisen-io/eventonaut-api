from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..basicauth import basic_auth
from ..schemas.static_table_schemas import StaticClient, StaticTableOutput
import uuid
import logging
from datetime import datetime
from .. import models
from ..static_enums import client

router = APIRouter(tags=["client_status"])

@router.post("/client_status", response_model=StaticTableOutput, status_code=status.HTTP_201_CREATED)
def create_client_status(static_client: StaticClient, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    client_dict = static_client.model_dump()
    client_dict["status"] = client_dict["status"].lower()
    db_static_client = models.ClientStatus(**client_dict)
    db_static_client.id = client.ClientEnum[db_static_client.status.upper()].value
    db_static_client.created_on = db_static_client.updated_on = datetime.utcnow()
    db_static_client.uuid = str(uuid.uuid4())
    db.add(db_static_client)
    try:
        db.commit()
    except:
        db.rollback()
        logging.exception("Status already exists")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Status already exists")
    db.refresh(db_static_client)
    db_static_client.status = db_static_client.status.upper()
    logging.info(f"Status created with id {db_static_client.uuid}")
    return db_static_client

@router.get("/client_status", response_model=list[StaticTableOutput])
def get_client_status(db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    static_client = db.query(models.ClientStatus).all()
    if static_client is None or len(static_client) == 0:
        logging.exception("no status found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no status found")
    logging.info("client status retrieved")
    return static_client

@router.delete("/client_status/{status_id}", response_model=StaticTableOutput)
def delete_client_status(status_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    static_client = db.query(models.ClientStatus).filter(models.ClientStatus.uuid == status_id).first()
    if static_client is None:
        logging.exception("status not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="status not found")
    db.delete(static_client)
    db.commit()
    logging.info(f"status deleted with id {static_client.uuid}")
    return True