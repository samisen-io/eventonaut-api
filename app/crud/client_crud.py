import logging
import os
from urllib.parse import urlparse
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.routers import upload_image
from .. import models
from ..schemas import client_schemas as schemas
from datetime import datetime
import uuid
from ..static_enums import client as client_enum

def create_client(db: Session, client: schemas.ClientCreate, user_id: int):
    client_dict = client.model_dump()
    client_status = client_dict.pop("status")
    client_profile_image_url = client_dict.pop("profile_image_url")
    db_client = models.Client(**client_dict)
    db_client.client_status_id = client_enum.ClientEnum[client_status.upper()].value
    db_client.created_on = datetime.utcnow()
    db_client.updated_on = datetime.utcnow()
    db_client.uuid = "cli-" + str(uuid.uuid4())
    db_client.owner_id = user_id
    
    if client_profile_image_url is not None:
        parsed_url = urlparse(client_profile_image_url)
        path = parsed_url.path
        filename_with_ext = os.path.basename(path)
        _, extension = os.path.splitext(filename_with_ext)

        if extension not in ['.jpg', '.jpeg', '.png']:
            logging.exception("Invalid image file format")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file format")
        
        image_url = upload_image.move_file_from_temporary_to_permanent_container(source_container_name="temporary-images", dest_container_name="client-logos", old_blob_name=filename_with_ext, new_blob_name=f"profile-{db_client.uuid}" + extension)
    
    db_client.profile_image_url = image_url
    
    db.add(db_client)
    try:
        db.commit()
    except Exception as e:
        upload_image.delete_blob("client-logos", f"profile-{db_client.uuid}" + extension)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_client)
    db_client.status = client_enum.ClientEnum(db_client.client_status_id).name
    return db_client

def get_client(db: Session, client_id: int):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    client.status = client_enum.ClientEnum(client.client_status_id).name
    return client

def get_client_by_email(db: Session, email: str):
    return db.query(models.Client).filter(models.Client.contact_email.ilike(email), models.Client.isarchived == False).first()

def get_client_by_uuid(db: Session, client_uuid: str):
    client = db.query(models.Client).filter(models.Client.uuid == client_uuid, models.Client.isarchived == False).first()
    client.status = client_enum.ClientEnum(client.client_status_id).name
    return client

def get_client_by_uuid_and_owner_id(db: Session, client_id: str, owner_id: int):
    return db.query(models.Client).filter(models.Client.uuid == client_id, models.Client.owner_id == owner_id, models.Client.isarchived == False).first()

def get_all_clients(db: Session, offset: int = 0, limit: int = 100):
    clients = db.query(models.Client).offset(offset).limit(limit).all()
    for client in clients:
        client.status = client_enum.ClientEnum(client.client_status_id).name
    return clients

def get_all_clients_by_owner_id(db: Session, owner_id:int, offset: int = 0, limit: int = 100):
    clients = db.query(models.Client).filter(models.Client.owner_id == owner_id, models.Client.isarchived == False).offset(offset).limit(limit).all()
    for client in clients:
        client.status = client_enum.ClientEnum(client.client_status_id).name
    return clients

def update_client(db: Session, client: schemas.ClientUpdate):
    db_client = db.query(models.Client).filter(models.Client.uuid == client.id).first()
    
    client_dict = client.model_dump()
    client_dict.pop("id")
    client_status = client_dict.pop("status")
    client_profile_image_url = client_dict.pop("profile_image_url")
    db_client.profile_image_url = client_dict.pop("profile_image_url")
    
    if client_status is not None:
        db_client.client_status_id = client_enum.ClientEnum[client_status.upper()].value
    
    for key, value in client_dict.items():
        if value is not None:
            setattr(db_client, key, value)
    
    if client_profile_image_url is not None:
        parsed_url = urlparse(client_profile_image_url)
        path = parsed_url.path
        filename_with_ext = os.path.basename(path)
        _, extension = os.path.splitext(filename_with_ext)

        if extension not in ['.jpg', '.jpeg', '.png']:
            logging.exception("Invalid image file format")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file format")
        
        image_url = upload_image.move_file_from_temporary_to_permanent_container(source_container_name="temporary-images", dest_container_name="client-logos", old_blob_name=filename_with_ext, new_blob_name=f"profile-{db_client.uuid}" + extension)
    
    db_client.profile_image_url = image_url
    
    db_client.updated_on = datetime.utcnow()
    try:
        db.commit()
    except Exception as e:
        if client_profile_image_url is not None:
            upload_image.delete_blob("client-logos", f"profile-{db_client.uuid}" + extension)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_client)
    db_client.status = client_enum.ClientEnum(db_client.client_status_id).name
    return db_client

def delete_client(db: Session, client_id: str):
    db_client = db.query(models.Client).filter(models.Client.uuid == client_id).first()
    if db_client is None:
        return False
    db_client.isarchived = True
    db.commit()
    return True