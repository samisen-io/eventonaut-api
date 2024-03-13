from fastapi import HTTPException
from fastapi import status as Status
from sqlalchemy.orm import Session
from ..models import EventDocuments
import logging
import uuid
from datetime import datetime

def insert_event_document(db: Session, conference_id: int, file_url: str):
    db_event_documemt = EventDocuments(conference_id=conference_id, document_url = file_url)
    db_event_documemt.uuid = str(uuid.uuid4())
    db_event_documemt.created_on = db_event_documemt.updated_on = datetime.utcnow()
    db.add(db_event_documemt)
    db.commit()
    db.refresh(db_event_documemt)
    return db_event_documemt

def get_event_documents_by_conference_id(db: Session, conference_id: int):
    return db.query(EventDocuments).filter(EventDocuments.conference_id == conference_id).all()

def delete_event_document(db: Session, event_document_id: str):
    event_document = db.query(EventDocuments).filter(EventDocuments.uuid == event_document_id).first()
    if not event_document:
        logging.exception(f"Document not found in the database with url: {event_document_id}")
        raise HTTPException(status_code=Status.HTTP_404_NOT_FOUND, detail="Document not found")
    db.delete(event_document)
    db.commit()
    return event_document