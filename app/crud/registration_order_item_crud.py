from datetime import datetime
from sqlalchemy.orm import Session
import uuid
import logging
from fastapi import HTTPException, status as Status
from app.models import RegistrationOrderItem
from app.schemas.registration_order_item_schema_temp import RegistrationOrderItemCreate
from ..code_generator import generate_unique_string

def get_registration_order_item_by_uuid(db: Session, uuid: str):
    return db.query(RegistrationOrderItem).filter(RegistrationOrderItem.uuid == uuid).first()

def get_registration_order_item_by_id(db: Session, id: int):
    return db.query(RegistrationOrderItem).filter(RegistrationOrderItem.id == id).first()

def create_registration_order_item(db: Session, registration_order_item: RegistrationOrderItemCreate):
    registration_order_item_db = RegistrationOrderItem(
        uuid='roi-'+str(uuid.uuid4()),
        registration_order_id=registration_order_item.registration_order_id,
        description=registration_order_item.description,
        quantity=registration_order_item.quantity,
        unit_price=registration_order_item.unit_price,
        total_amount=registration_order_item.total_amount,
        type=registration_order_item.type,
        code=registration_order_item.code,
        created_on=datetime.now(),
        updated_on=datetime.now()
    )
    db.add(registration_order_item_db)
    db.commit()
    db.refresh(registration_order_item_db)
    return registration_order_item_db

def delete_registration_order_item(db: Session, uuid: str):
    registration_order_item = get_registration_order_item_by_uuid(db, uuid)
    if registration_order_item is None:
        raise HTTPException(status_code=Status.HTTP_404_NOT_FOUND, detail="Registration order item not found")
    db.delete(registration_order_item)
    db.commit()
    return registration_order_item