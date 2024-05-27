from fastapi import APIRouter, HTTPException, status, Depends, Security, UploadFile, File
from sqlalchemy.orm import Session
from .. dependencies import get_db
from ..oauth2 import get_current_active_user
from .upload_image import upload_file, delete_blob_by_url
from ..schemas.user_schemas import UserAuthentication as User
from ..crud import template_crud as crud
from ..schemas.template_schemas import TemplateResponse
import logging
from ..static_enums.role import RoleEnum

router = APIRouter(
    tags=['template'],
    prefix='/template'
)

@router.post('/upload' ,response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def upload_templte(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name])):
    file_extension = file.filename.split(".")[-1]
    if file_extension != "pug":
        logging.exception(f"Invalid file type")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type")
    organization_id = current_user.organization_user[0].organization_id
    original_filename = file.filename
    file.filename = f'{current_user.uuid}-{original_filename}'
    uploaded_file = upload_file(file, db)
    blob_url = uploaded_file['url']
    
    response = crud.insert_template(db = db, template_url = blob_url, organization_id = organization_id, template_name=original_filename)
    logging.info(f"Template uploaded successfully")
    return response

@router.get('/all', response_model=list[TemplateResponse])
async def get_all_templates(db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name])):
    organization_id = current_user.organization_user[0].organization_id
    templates = crud.get_templates(db, organization_id)
    if not templates or len(templates) == 0:
        logging.exception(f"No templates found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No templates found")
    logging.info(f"Templates retrieved successfully")
    return crud.get_templates(db, organization_id)

@router.get('/{template_id}', response_model=TemplateResponse)
async def get_template_by_id(template_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name])):
    organization_id = current_user.organization_user[0].organization_id
    template = crud.get_template_by_id(db, template_id, organization_id)
    if not template:
        logging.exception(f"Template not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return template

@router.delete('/{template_id}')
async def delete_template(template_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name])):
    organization_id = current_user.organization_user[0].organization_id
    template = crud.get_template_by_id(db, template_id, organization_id)
    if not template:
        logging.exception(f"Template not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    crud.delete_template(db, template)
    delete_blob_by_url(template.template_url)
    logging.info(f"Template deleted successfully")
    return {"message": "Template deleted successfully"}