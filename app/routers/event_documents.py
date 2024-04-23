import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, File, Security
from ..dependencies import get_db
from sqlalchemy.orm import Session
from .upload_image import upload_file, check_for_blob_in_container, delete_blob_by_url
from app.oauth2 import get_current_active_user
from ..crud import conferences_crud
from app.schemas.user_schemas import UserAuthentication as User
from ..crud import event_documents_crud as crud
from ..schemas.event_document_schemas import EventDocumentRequest, EventDocumentResponse
from ..static_enums.blob_container_enums import BlobContainer
from fastapi.encoders import jsonable_encoder
from app.static_enums.role import RoleEnum

router = APIRouter(tags=["event_documents"], prefix="/event_documents")

@router.post("/", response_model=EventDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_event_document(conference_id: str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name, "organizer"])):
    try:
        conference = conferences_crud.get_conference_by_uuid(db, conference_id, current_user.id)
        
        original_file_name = file.filename
        file.filename = f'{conference.uuid}-{file.filename}'
        uploaded_file = upload_file(file, db)
        blob_url = uploaded_file["url"]
        
        content_type = file.headers["content-type"]
        size = file.size / (1024 * 1024)
        request = EventDocumentRequest(conference_id=conference.id, 
                                        file_url=blob_url, 
                                        original_file_name=original_file_name,
                                        content_type=content_type, 
                                        size=size)
        
        response = crud.insert_event_document(db= db, request= request)
        
        return map_event_document_response(conference_id, response)
    
    except HTTPException as e:
        logging.error(f"An error occurred while creating event document: {str(e)}")
        raise e    
    except Exception as e:
        logging.error(f"An error occurred while creating event document: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail = jsonable_encoder(str(e)))

def map_event_document_response(conference_id, response):
    return EventDocumentResponse(uuid=response.uuid, 
                                     conference_uuid=conference_id,
                                     document_url=response.document_url, 
                                     name=response.name, 
                                     content_type=response.content_type, 
                                     size=f"{str(response.size)} MB")

@router.get("/{conference_id}", response_model=list[EventDocumentResponse])
def get_all_event_documents(conference_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ATTENDEE.name,"organizer", "attendee"])):
    if current_user.role == "organizer":
        conference = conferences_crud.get_conference_by_uuid(db, conference_id, current_user.id)
    elif current_user.role == "attendee":
        conference = conferences_crud.get_conference(db, conference_id)
    documents = crud.get_event_documents_by_conference_id(db, conference.id)
    if len(documents) == 0:
        logging.exception(f"No documents found for conference with id: {conference_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents found")
    return [map_event_document_response(conference_id, document) for document in documents]

@router.delete("/")
def delete_event_document(event_document_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name, "organizer"])):
    try:
        deleted_event_document = crud.delete_event_document(db, event_document_id)
        delete_blob_by_url(deleted_event_document.document_url)
        return {"message": "Document deleted successfully"}
    except HTTPException as e:
        logging.error(f"An error occurred while deleting event document: {str(e)}")
        raise e
    except Exception as e:
        logging.exception(f"Error deleting document: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail= jsonable_encoder(str(e)))