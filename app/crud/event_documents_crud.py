from sqlalchemy.orm import Session
from ..models import EventDocuments
import logging
import uuid
from datetime import datetime

def insert_event_document(db: Session, conference_id: int, file_url: str):
    db_event_documemt = EventDocuments(conference_id=conference_id, document_url = file_url)
    db_event_documemt.uuid = str(uuid.uuid4())
    db_event_documemt.created_on = updated_on = datetime.utcnow()
    db.add(db_event_documemt)
    db.commit()
    db.refresh(db_event_documemt)
    return db_event_documemt

def get_event_documents_by_conference_id(db: Session, conference_id: int):
    return db.query(EventDocuments).filter(EventDocuments.conference_id == conference_id).all()