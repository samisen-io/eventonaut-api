from sqlalchemy.orm import Session
from app.schemas.session_document_schemas import SessionDocumentRequest
from ..models import SessionDocuments
import uuid
from datetime import datetime
import logging
from fastapi import HTTPException, status as Status

def get_all_session_documents_by_organization(db: Session, organization_id: int, offset: int = 0, limit: int = 100):
    return db.query(SessionDocuments).filter(SessionDocuments.organization_id == organization_id).offset(offset).limit(limit).all()

def insert_session_document(db: Session, request: SessionDocumentRequest):
    db_doc = db.query(SessionDocuments).filter(SessionDocuments.document_url == request.document_url).first()
    if db_doc:
        db_doc.content_type = request.content_type
        db_doc.size = request.size
        db_doc.name = request.original_file_name
        db_doc.updated_on = datetime.utcnow()
        db.commit()
        db.refresh(db_doc)
        return db_doc
    
    db_session_documemt = SessionDocuments(session_id=request.session_id, 
                                           document_url = request.document_url, 
                                           name = request.original_file_name, 
                                           content_type = request.content_type, 
                                           size = request.size)
    db_session_documemt.uuid = "sdo-"+str(uuid.uuid4())
    db_session_documemt.created_on = db_session_documemt.updated_on = datetime.utcnow()
    db.add(db_session_documemt)
    db.commit()
    db.refresh(db_session_documemt)
    return db_session_documemt

def get_session_documents_by_session_id(db: Session, session_id: int): 
    return db.query(SessionDocuments).filter(SessionDocuments.session_id == session_id).order_by(SessionDocuments.updated_on.desc()).all()

def delete_session_document(db: Session, session_id: str):
    session_document = db.query(SessionDocuments).filter(SessionDocuments.uuid == session_id).first()
    if not session_document:
        logging.exception(f"Document not found in the database with url: {session_id}")
        raise HTTPException(status_code=Status.HTTP_404_NOT_FOUND, detail="Document not found")
    db.delete(session_document)
    db.commit()
    return session_document