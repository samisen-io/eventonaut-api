from datetime import datetime
import uuid
from app.schemas.registratin_setup_item_schema_temp import RegistrationSetupItemCreateTemp, RegistrationSetupItemTemp, RegistrationSetupItemUpdateTemp
from ..import models
from sqlalchemy.orm import Session, joinedload

def create_registration_setup_item(db: Session, registration_setup_item: RegistrationSetupItemCreateTemp):
    db_registration_setup_item = models.RegistrationSetupItem(
        uuid = 'ticket-'+str(uuid.uuid4()),
        name = registration_setup_item.name,
        description = registration_setup_item.description,
        registration_setup_id = registration_setup_item.registration_setup_id,
        price = registration_setup_item.price,
        available_from = registration_setup_item.available_from,
        available_to = registration_setup_item.available_to,
        image_url = registration_setup_item.image_url,
        product_id = registration_setup_item.product_id,
        total_quantity = registration_setup_item.total_quantity,
        available_quantity = registration_setup_item.total_quantity,
        created_on = datetime.now(),
        updated_on = datetime.now()
    )
    db.add(db_registration_setup_item)
    db.commit()
    db.refresh(db_registration_setup_item)
    return db_registration_setup_item

def get_registration_setup_item(db: Session, registration_setup_item_id: int):
    return db.query(models.RegistrationSetupItem).filter(models.RegistrationSetupItem.id == registration_setup_item_id).first()

def get_registration_setup_items_by_event_id(db: Session, event_id: int):
    return db.query(models.RegistrationSetupItem).join(models.RegistrationSetup).filter(models.RegistrationSetup.event_id == event_id).all()

def get_registraion_setup_items_using_uuid(db: Session, registration_setup_item_uuid: str):
    return db.query(models.RegistrationSetupItem).filter(models.RegistrationSetupItem.uuid == registration_setup_item_uuid).first()

def update_registration_setup_item(db: Session, registration_setup_item: models.RegistrationSetupItem):
    db.query(models.RegistrationSetupItem).filter(models.RegistrationSetupItem.id == registration_setup_item.id).update({
        models.RegistrationSetupItem.name: registration_setup_item.name,
        models.RegistrationSetupItem.description: registration_setup_item.description,
        models.RegistrationSetupItem.registration_setup_id: registration_setup_item.registration_setup_id,
        models.RegistrationSetupItem.price: registration_setup_item.price,
        models.RegistrationSetupItem.available_from: registration_setup_item.available_from,
        models.RegistrationSetupItem.available_to: registration_setup_item.available_to,
        models.RegistrationSetupItem.image_url: registration_setup_item.image_url,
        models.RegistrationSetupItem.product_id: registration_setup_item.product_id,
        models.RegistrationSetupItem.total_quantity: registration_setup_item.total_quantity,
        models.RegistrationSetupItem.available_quantity: registration_setup_item.available_quantity,
        models.RegistrationSetupItem.updated_on: datetime.now()
    })
    db.commit()
    return db.query(models.RegistrationSetupItem).filter(models.RegistrationSetupItem.id == registration_setup_item.id).first()