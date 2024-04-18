from fastapi import HTTPException
from fastapi import status as Status
from sqlalchemy.orm import Session

from app.schemas.event_document_schemas import EventDocumentRequest
from ..models import EventDocuments
import logging
import uuid
from datetime import datetime

def insert_event_document(db: Session, request: EventDocumentRequest):
    db_doc = db.query(EventDocuments).filter(EventDocuments.document_url == request.file_url).first()
    if db_doc:
        db_doc.content_type = request.content_type
        db_doc.size = request.size
        db_doc.name = request.original_file_name
        db_doc.updated_on = datetime.utcnow()
        db.commit()
        db.refresh(db_doc)
        return db_doc
    
    db_event_documemt = EventDocuments(conference_id=request.conference_id, 
                                       document_url = request.file_url,
                                       name = request.original_file_name,
                                       content_type = request.content_type,
                                       size = request.size)
    db_event_documemt.uuid =  "etd-"+ str(uuid.uuid4())
    db_event_documemt.created_on = db_event_documemt.updated_on = datetime.utcnow()
    db.add(db_event_documemt)
    db.commit()
    db.refresh(db_event_documemt)
    return db_event_documemt

def get_event_documents_by_conference_id(db: Session, conference_id: int):
    return db.query(EventDocuments).filter(EventDocuments.conference_id == conference_id).order_by(EventDocuments.updated_on.desc()).all()

def delete_event_document(db: Session, event_document_id: str):
    event_document = db.query(EventDocuments).filter(EventDocuments.uuid == event_document_id).first()
    if not event_document:
        logging.exception(f"Document not found in the database with url: {event_document_id}")
        raise HTTPException(status_code=Status.HTTP_404_NOT_FOUND, detail="Document not found")
    db.delete(event_document)
    db.commit()
    return event_document