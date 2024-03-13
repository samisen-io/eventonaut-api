from sqlalchemy.orm import Session

from app.schemas.event_document_schemas import EventDocumentRequest
from ..models import EventDocuments
import logging
import uuid
from datetime import datetime

def insert_event_document(db: Session, request: EventDocumentRequest):
    db_event_documemt = EventDocuments(conference_id=request.conference_id, 
                                       document_url = request.file_url,
                                       name = request.file_name,
                                       content_type = request.content_type,
                                       size = request.size)
    db_event_documemt.uuid = str(uuid.uuid4())
    db_event_documemt.created_on = db_event_documemt.updated_on = datetime.utcnow()
    db.add(db_event_documemt)
    db.commit()
    db.refresh(db_event_documemt)
    return db_event_documemt

def get_event_documents_by_conference_id(db: Session, conference_id: int):
    return db.query(EventDocuments).filter(EventDocuments.conference_id == conference_id).all()

def delete_event_document(db: Session, blob_url: str):
    event_document = db.query(EventDocuments).filter(EventDocuments.document_url == blob_url).first()
    if not event_document:
        logging.exception(f"Document not found in the database with url: {blob_url}")
        return False
    db.delete(event_document)
    db.commit()
    return True