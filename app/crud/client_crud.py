import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.routers import upload_image
from .. import models
from ..schemas import client_schemas as schemas
from datetime import datetime
import uuid
from ..static_enums import client as client_enum
from ..static_enums.blob_container_enums import BlobContainer

def get_all_clients_by_organization_id(db: Session, organization_id: int, offset: int = 0, limit: int = 100):
    clients = db.query(models.Client).filter(models.Client.organization_id == organization_id).order_by(models.Client.updated_on.desc()).offset(offset).limit(limit).all()
    return clients

def create_client(db: Session, client: schemas.ClientCreate, user_id: int):
    client_dict = client.model_dump()
    client_status = client_dict.pop("status")
    client_profile_image_url = client_dict.pop("profile_image_url")
    db_client = models.Client(**client_dict)
    db_client.client_status_id = client_enum.ClientEnum[client_status].value
    db_client.created_on = datetime.utcnow()
    db_client.updated_on = datetime.utcnow()
    db_client.uuid = "cli-" + str(uuid.uuid4())
    db_client.owner_id = user_id
    
    db_client.profile_image_url = upload_image.get_actual_url(image_url=client_profile_image_url, new_blob_container=BlobContainer.CLIENT_LOGOS.value, new_blob_name=f"profile-{db_client.uuid}") if client_profile_image_url is not None else None
    
    db.add(db_client)
    try:
        db.commit()
    except Exception as e:
        upload_image.delete_blob_by_url(db_client.profile_image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_client)
    return db_client

def get_client(db: Session, client_id: int):
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    return client

def get_client_by_uuid(db: Session, client_uuid: str):
    client = db.query(models.Client).filter(models.Client.uuid == client_uuid, models.Client.is_archived == False).first()
    return client

def get_client_by_uuid_and_owner_id(db: Session, client_id: str, owner_id: int):
    return db.query(models.Client).filter(models.Client.uuid == client_id, models.Client.owner_id == owner_id, models.Client.is_archived == False).first()

def get_all_clients(db: Session, offset: int = 0, limit: int = 100):
    clients = db.query(models.Client).order_by(models.Client.updated_on.desc()).offset(offset).limit(limit).all()
    return clients

def get_all_clients_by_owner_id(db: Session, owner_id:int, offset: int = 0, limit: int = 100):
    clients = db.query(models.Client).filter(models.Client.owner_id == owner_id, models.Client.is_archived == False).order_by(models.Client.updated_on.desc()).offset(offset).limit(limit).all()
    return clients

def update_client(db: Session, client: schemas.ClientUpdate):
    db_client = db.query(models.Client).filter(models.Client.uuid == client.id).first()
    
    client_dict = client.model_dump()
    client_dict.pop("id")
    client_status = client_dict.pop("status")
    client_profile_image_url = client_dict.pop("profile_image_url")
    
    if client_status is not None:
        db_client.client_status_id = client_enum.ClientEnum[client_status.upper()].value
    
    for key, value in client_dict.items():
        if value is not None:
            setattr(db_client, key, value)
    
    if client_profile_image_url is not None and upload_image.get_container_name_from_url(client_profile_image_url) != BlobContainer.CLIENT_LOGOS.value:
        db_client.profile_image_url = upload_image.get_actual_url(image_url=client_profile_image_url, new_blob_container=BlobContainer.CLIENT_LOGOS.value, new_blob_name=f"profile-{db_client.uuid}")
    elif client_profile_image_url is None and db_client.profile_image_url is not None:
        upload_image.delete_blob_by_url(db_client.profile_image_url)
        db_client.profile_image_url = None
    
    db_client.updated_on = datetime.utcnow()
    try:
        db.commit()
    except Exception as e:
        if client_profile_image_url is not None:
            upload_image.delete_blob_by_url(db_client.profile_image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_client)
    return db_client

def delete_client(db: Session, client_id: str):
    db_client = db.query(models.Client).filter(models.Client.uuid == client_id).first()
    
    if db_client is None:
        return False

    if db_client.conferences and any([conference.is_archived == False for conference in db_client.conferences]):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot delete client with existing conference relationship")

    db_client.is_archived = True
    db.commit()
    return True