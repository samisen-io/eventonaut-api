from fastapi import HTTPException
from fastapi import status as Status
from sqlalchemy.orm import Session
from app.schemas.exhibitor_document_schemas import ExhibitorDocumentRequest
from ..models import ExhibitorDocuments
import logging
import uuid
from datetime import datetime

def insert_exhibitor_document(db: Session, request: ExhibitorDocumentRequest):
    db_doc = db.query(ExhibitorDocuments).filter(ExhibitorDocuments.document_url == request.file_url).first()
    if db_doc:
        db_doc.content_type = request.content_type
        db_doc.size = request.size
        db_doc.name = request.original_file_name
        db_doc.updated_on = datetime.utcnow()
        db.commit()
        db.refresh(db_doc)
        return db_doc
    
    db_exhibitor_document = ExhibitorDocuments(exhibitor_id=request.exhibitor_id,
                                       document_url = request.file_url,
                                       name = request.original_file_name,
                                       content_type = request.content_type,
                                       size = request.size)
    db_exhibitor_document.uuid =  "exd-"+ str(uuid.uuid4())
    db_exhibitor_document.created_on = db_exhibitor_document.updated_on = datetime.utcnow()
    db.add(db_exhibitor_document)
    db.commit()
    db.refresh(db_exhibitor_document)
    return db_exhibitor_document

def get_exhibitor_documents_by_exhibitor_id(db: Session, exhibitor_id: int):
    return db.query(ExhibitorDocuments).filter(ExhibitorDocuments.exhibitor_id == exhibitor_id).order_by(ExhibitorDocuments.updated_on.desc()).all()

def delete_exhibitor_document(db: Session, exhibitor_document_id: str):
    exhibitor_document = db.query(ExhibitorDocuments).filter(ExhibitorDocuments.uuid == exhibitor_document_id).first()
    if not exhibitor_document:
        logging.exception(f"Document not found in the database with url: {exhibitor_document_id}")
        raise HTTPException(status_code=Status.HTTP_404_NOT_FOUND, detail="Document not found")
    db.delete(exhibitor_document)
    db.commit()
    return exhibitor_document