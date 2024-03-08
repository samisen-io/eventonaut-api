from sqlalchemy.orm import Session
from ..models import SessionDocuments
import uuid
from datetime import datetime
import logging

def insert_session_document(db: Session, session_id: int, file_url: str):
    db_session_documemt = SessionDocuments(session_id=session_id, document_url = file_url)
    db_session_documemt.uuid = str(uuid.uuid4())
    db_session_documemt.created_on = db_session_documemt.updated_on = datetime.utcnow()
    db.add(db_session_documemt)
    db.commit()
    db.refresh(db_session_documemt)
    return db_session_documemt

def get_session_documents_by_session_id(db: Session, session_id: int): 
    return db.query(SessionDocuments).filter(SessionDocuments.session_id == session_id).all()

def delete_session_document(db: Session, blob_url: str):
    session_document = db.query(SessionDocuments).filter(SessionDocuments.document_url == blob_url).first()
    if not session_document:
        logging.exception(f"Document not found in the database with url: {blob_url}")
        return False
    db.delete(session_document)
    db.commit()
    return True