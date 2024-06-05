import logging
import uuid
from fastapi import APIRouter, HTTPException,status,Depends,Security,UploadFile,File

from app.basicauth import basic_auth
from ..crud import master_template_crud as crud
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.routers.upload_image import upload_file
from app.schemas.template_schemas import TemplateResponse


router = APIRouter(
    tags=['master_template'],
    prefix='/master_template'
)

@router.post('/upload', response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def upload_template(file: UploadFile = File(...), db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    file_extension = file.filename.split(".")[-1]
    if file_extension != "pug":
        logging.exception('Invalid file type')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type")
    original_filename = file.filename
    file.filename = f'{'usr-'+str(uuid.uuid4())}-{original_filename}'
    uploaded_file = upload_file(file, db)
    blob_url = uploaded_file['url']
    response = crud.insert_master_template(db=db, template_name=original_filename, template_url=blob_url)
    logging.info('Template uploaded successfully')  
    return response

@router.get('/all', response_model=list[TemplateResponse])
async def get_all_templates(db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    templates = crud.get_master_templates(db)
    if not templates or len(templates) == 0:
        logging.exception('No templates found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No templates found")
    logging.info('Templates retrieved successfully')
    return templates

@router.get('/{template_id}', response_model=TemplateResponse)
async def get_template_by_id(template_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    template = crud.get_master_template_by_id(db, template_id)
    if not template:
        logging.exception('Template not found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return template

@router.delete('/{template_id}')
async def delete_template(template_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    template = crud.get_master_template_by_id(db, template_id)
    if not template:
        logging.exception('Template not found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    crud.delete_master_template(db, template)
    logging.info('Template deleted successfully')
    return {"message": "Template deleted successfully"}