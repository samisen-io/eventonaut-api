from sqlalchemy.orm import Session
from .. import models
from ..schemas import client_schemas as schemas
from datetime import datetime
import uuid

def create_client(db: Session, client: schemas.ClientCreate, user_id: int):
    db_client = models.Client(**client.model_dump())
    db_client.created_on = datetime.utcnow()
    db_client.updated_on = datetime.utcnow()
    db_client.uuid = "cli-" + str(uuid.uuid4())
    db_client.owner_id = user_id
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

def get_client(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id).first()

def get_client_by_email(db: Session, email: str):
    return db.query(models.Client).filter(models.Client.contact_email.ilike(email)).first()

def get_client_by_uuid(db: Session, client_uuid: str):
    return db.query(models.Client).filter(models.Client.uuid == client_uuid).first()

def get_client_by_uuid_and_owner_id(db: Session, client_id: str, owner_id: int):
    return db.query(models.Client).filter(models.Client.uuid == client_id, models.Client.owner_id == owner_id).first()

def get_all_clients(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.Client).offset(offset).limit(limit).all()

def update_client(db: Session, client: schemas.ClientUpdate):
    db_client = db.query(models.Client).filter(models.Client.uuid == client.id).first()
    
    updates = {
        'name': client.name,
        'contact_name': client.contact_name,
        'contact_email': client.contact_email,
        'contact_phone': client.contact_phone,
        'profile_image_url': client.profile_image_url,
        'address': client.address,
        'status': client.status
    }
    
    for key, value in updates.items():
        if value is not None:
            setattr(db_client, key, value)
    
    db_client.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_client)
    return db_client

def delete_client(db: Session, client_id: str):
    db_client = db.query(models.Client).filter(models.Client.uuid == client_id).first()
    if db_client is None:
        return False
    db.delete(db_client)
    db.commit()
    return True