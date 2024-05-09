from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, File, Security
from ..dependencies import get_db
from sqlalchemy.orm import Session
from .upload_image import upload_file, delete_blob_by_url
from app.oauth2 import get_current_active_user
from ..crud import exhibitor_documents_crud as crud, exhibitor_crud
from app.schemas.user_schemas import UserAuthentication as User
from ..schemas.exhibitor_document_schemas import ExhibitorDocumentRequest, ExhibitorDocumentResponse
import logging
from app.static_enums.role import RoleEnum

router = APIRouter(tags=["exhibitor_documents"], prefix="/exhibitor_documents")

@router.post("/", response_model=ExhibitorDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_exhibitor_document(exhibitor_id: str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name, "organizer"])):
    try:
        organization_id = current_user.organization_user[0].organization_id
        exhibitor = exhibitor_crud.get_exhibitor_by_id(db, exhibitor_id, organization_id)
        
        if exhibitor is None:
            logging.exception(f"Exhibitor not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibitor not found")
        
        original_file_name = file.filename
        file.filename = f'{exhibitor.uuid}-{file.filename}'
        uploaded_file = upload_file(file, db)
        blob_url = uploaded_file["url"]
        
        content_type = file.headers["content-type"]
        size = file.size / (1024 * 1024)
        request = ExhibitorDocumentRequest(exhibitor_id=exhibitor.id,
                                        file_url=blob_url, 
                                        original_file_name=original_file_name,
                                        content_type=content_type, 
                                        size=size)
        
        response = crud.insert_exhibitor_document(db= db, request = request)
        
        return map_exhibitor_document_response(exhibitor_id, response)
    
    except HTTPException as e:
        logging.error(f"An error occurred while creating exhibitor document: {str(e)}")
        raise e    
    except Exception as e:
        logging.error(f"An error occurred while creating exhibitor document: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail = str(e))
    
def map_exhibitor_document_response(exhibitor_id, response):
    return ExhibitorDocumentResponse(uuid=response.uuid, 
                                     exhibitor_uuid=exhibitor_id,
                                     document_url=response.document_url, 
                                     name=response.name, 
                                     content_type=response.content_type, 
                                     size=f"{str(response.size)} MB")
    
@router.get("/{exhibitor_id}", response_model=list[ExhibitorDocumentResponse])
def get_all_exhibitor_documents(exhibitor_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ATTENDEE.name,"organizer", "attendee"])):
    roles = [user_role.role for user_role in current_user.user_roles]
    if roles[0].name == RoleEnum.ATTENDEE.name:
        exhibitor = exhibitor_crud.get_exhibitor_by_uuid(db, exhibitor_id)
    elif roles[0].name == RoleEnum.ORGANIZATION_ADMIN.name or roles[0].name == RoleEnum.ORGANIZATION_USER.name:
        organization_id = current_user.organization_user[0].organization_id
        exhibitor = exhibitor_crud.get_exhibitor_by_id(db, exhibitor_id, organization_id)
    documents = crud.get_exhibitor_documents_by_exhibitor_id(db, exhibitor.id)
    if len(documents) == 0:
        logging.exception(f"No documents found for conference with id: {exhibitor_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No documents found")
    return [map_exhibitor_document_response(exhibitor_id, document) for document in documents]

@router.delete("/")
def delete_exhibitor_document(exhibitor_document_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name, "organizer"])):
    try:
        deleted_exhibitor_document = crud.delete_exhibitor_document(db, exhibitor_document_id)
        delete_blob_by_url(deleted_exhibitor_document.document_url)
        return {"message": "Document deleted successfully"}
    except HTTPException as e:
        logging.error(f"An error occurred while deleting exhibitor document: {str(e)}")
        raise e
    except Exception as e:
        logging.exception(f"Error deleting document: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail= str(e))