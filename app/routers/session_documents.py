from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, File, Security

from app import models
from ..dependencies import get_db
from sqlalchemy.orm import Session
from .upload_image import upload_file, check_for_blob_in_container, delete_blob_by_url
from app.oauth2 import get_current_active_organization, get_current_active_user
from ..crud import sessions_crud
from app.schemas.user_schemas import UserAuthentication as User
from ..crud import session_document_crud as crud
from ..schemas.session_document_schemas import SessionDocumentResponse, SessionDocumentRequest
from ..static_enums.blob_container_enums import BlobContainer
import logging
from app.static_enums.role import RoleEnum
from app.static_enums.role import RoleEnum

router = APIRouter(tags=["session_documents"], prefix="/session_documents")

@router.post("/", response_model=SessionDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_session_document(session_id: str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name,"organizer"])):
    try:
        session = sessions_crud.get_session_by_uuid_id(db, session_id, current_user.id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        
        original_file_name = file.filename
        file.filename = f'{session.uuid}-{file.filename}'
        uploaded_file = upload_file(file, db)
        blob_url = uploaded_file["url"]
        
        request = SessionDocumentRequest(session_id=session.id, 
                                            document_url=blob_url, 
                                            original_file_name=original_file_name, 
                                            content_type=file.content_type, 
                                            size=file.size / (1024 * 1024))
        
        response = crud.insert_session_document(db, request)
        
        return map_session_document_response(session_id, response)
    except HTTPException as e:
        logging.error(f"An error occurred while creating session document: {str(e)}")
        raise e
    except Exception as e:
        logging.error(f"An error occurred while creating session document: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail= f"{str(e)}")

def map_session_document_response(session_id, response):
    return SessionDocumentResponse( uuid=response.uuid, 
                                     session_uuid =session_id,
                                     document_url=response.document_url, 
                                     name=response.name, 
                                     content_type=response.content_type, 
                                     size=f"{str(response.size)} MB")
    
@router.get("/by_organization", response_model=list[SessionDocumentResponse])
def get_all_session_documents_by_organization(offset: int = 0, limit: int = 100,db: Session = Depends(get_db), organization: models.Organization = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
    documents = crud.get_all_session_documents_by_organization(db, organization.id, offset, limit)
    if len(documents) == 0:
        logging.exception("No documents found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents found")
    return [map_session_document_response(document.session_id, document) for document in documents]

@router.get("/{session_id}", response_model=list[SessionDocumentResponse])
def get_all_session_documents(session_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, RoleEnum.ATTENDEE.name, "organizer", "attendee"])):
    if current_user.role == "organizer":
        session = sessions_crud.get_session_by_uuid_id(db, session_id, current_user.id)
    elif current_user.role == "attendee":
        session = sessions_crud.get_session_by_session_uuid(db, session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    documents = crud.get_session_documents_by_session_id(db, session.id)
    if len(documents) == 0:
        logging.exception(f"No documents found for session with id: {session_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents found")
    return [map_session_document_response(session_id, document) for document in documents]

@router.delete("/event_documents")
def delete_session_document(session_document_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])): 
    try:
        delete_session_document = crud.delete_session_document(db, session_document_id)
        delete_blob_by_url(delete_session_document.document_url)
        return {"message": "Document deleted successfully"}
    except HTTPException as e:
        logging.error(f"An error occurred while deleting session document: {str(e)}")
        raise e
    except Exception as e:
        logging.error(f"An error occurred while deleting session document: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail= f"{str(e)}")