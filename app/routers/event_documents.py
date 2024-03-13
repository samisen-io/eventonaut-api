import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, File, Security
from ..dependencies import get_db
from sqlalchemy.orm import Session
from .upload_image import upload_file, check_for_blob_in_container, delete_blob_by_url
from app.oauth2 import get_current_active_user
from ..crud import conferences_crud
from app.schemas.user_schemas import UserAuthentication as User
from ..crud import event_documents_crud as crud
from ..schemas.event_document_schemas import EventDocumentResponse
from ..static_enums.blob_container_enums import BlobContainer

router = APIRouter(tags=["event_documents"], prefix="/event_documents")

@router.post("/", response_model=EventDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_event_document(conference_id: str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    conference = conferences_crud.get_conference_by_uuid(db, conference_id, current_user.id)
    file.filename = f"evt-doc-{file.filename}"
    uploaded_file = upload_file(file, db)
    blob_url = uploaded_file["url"]

    return crud.insert_event_document(db, conference.id, blob_url)

@router.get("/{conference_id}", response_model=list[EventDocumentResponse])
def get_all_event_documents(conference_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    conference = conferences_crud.get_conference_by_uuid(db, conference_id, current_user.id)
    documents = crud.get_event_documents_by_conference_id(db, conference.id)
    if len(documents) == 0:
        logging.exception(f"No documents found for conference with id: {conference_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents found")
    return documents

@router.delete("/")
def delete_event_document(event_document_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    try:
        deleted_event_document = crud.delete_event_document(db, event_document_id)
        delete_blob_by_url(deleted_event_document.document_url)
        return {"message": "Document deleted successfully"}
    except Exception as e:
        logging.exception(f"Error deleting document: {e}")
        raise HTTPException(status_code=e.status_code, detail=f"{str(e.detail)}")