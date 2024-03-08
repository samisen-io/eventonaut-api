from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, File, Security
from ..dependencies import get_db
from sqlalchemy.orm import Session
from .upload_image import upload_file, check_for_blob_in_container, delete_blob_by_url
from app.oauth2 import get_current_active_user
from ..crud import sessions_crud
from app.schemas.user_schemas import UserAuthentication as User
from ..crud import session_document_crud as crud
from ..schemas.session_document_schemas import SessionDocumentResponse
from ..static_enums.blob_container_enums import BlobContainer
import logging

router = APIRouter(tags=["session_documents"], prefix="/session_documents")

@router.post("/", response_model=SessionDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_session_document(session_id: str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    session = sessions_crud.get_session_by_uuid_id(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    file.filename = f"ses-doc-{file.filename}"
    uploaded_file = upload_file(file, db)
    blob_url = uploaded_file["url"]
    
    return crud.insert_session_document(db, session.id, blob_url)

@router.get("/{session_id}", response_model=list[SessionDocumentResponse])
def get_all_session_documents(session_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    session = sessions_crud.get_session_by_uuid_id(db, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    documents = crud.get_session_documents_by_session_id(db, session.id)
    if len(documents) == 0:
        logging.exception(f"No documents found for session with id: {session_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents found")
    return documents

@router.delete("/event_documents")
def delete_session_document(blob_url: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    if not check_for_blob_in_container(blob_url, BlobContainer.SESSION_DOCUMENTS.value):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    crud.delete_session_document(db, blob_url)
    delete_blob_by_url(blob_url)
    return {"message": "Document deleted successfully"}