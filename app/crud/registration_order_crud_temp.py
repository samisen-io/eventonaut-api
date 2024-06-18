from datetime import datetime
import uuid
from fastapi import HTTPException, status as Status
from sqlalchemy.orm import Session
from fastapi.params import Depends

from app.models import RegistrationOrder
from app.schemas.registration_order_item_schema_temp import RegistrationOrderItem
from app.schemas.registration_order_schema_temp import RegistrationOrderCreate
from ..code_generator import generate_unique_string

def get_registration_order_by_order_id(db: Session, order_id: str):
    return db.query(RegistrationOrder).filter(RegistrationOrder.order_id == order_id).first()

def get_registration_order_by_uuid(db: Session, uuid: str):
    return db.query(RegistrationOrder).filter(RegistrationOrder.uuid == uuid).first()

def get_registration_order_by_id(db: Session, id: int):
    return db.query(RegistrationOrder).filter(RegistrationOrder.id == id).first()

def get_all_registration_orders_by_attendee_id(db: Session, attendee_id: int):
    return db.query(RegistrationOrder).filter(RegistrationOrder.attendee_id == attendee_id).all()

def create_registration_order(db: Session, registration_order: RegistrationOrderCreate):
    registration_order_db = RegistrationOrder(
        uuid='reo-'+str(uuid.uuid4()),
        event_id=registration_order.event_id,
        attendee_id=registration_order.attendee_id,
        amount=registration_order.amount,
        tax_amount=registration_order.tax_amount,
        fee_amount=registration_order.fee_amount,
        total_amount = registration_order.amount + registration_order.tax_amount + registration_order.fee_amount,
        created_on = datetime.now(),
        updated_on=datetime.now()
    )
    db.add(registration_order_db)
    db.commit()
    db.refresh(registration_order_db)
    return registration_order_db

def create_registration_order_temp(db: Session, registration_order: RegistrationOrderCreate):
    registration_order_db = RegistrationOrder(
        uuid='reo-'+str(uuid.uuid4()),
        event_id=registration_order.event_id,
        attendee_id=registration_order.attendee_id,
        amount=0,
        tax_amount=0,
        fee_amount=0,
        total_amount = 0,
        created_on = datetime.now(),
        updated_on=datetime.now()
    )
    db.add(registration_order_db)
    db.commit()
    db.refresh(registration_order_db)
    return registration_order_db

def update_registration_order(db: Session, registration_order: RegistrationOrder):
    db.query(RegistrationOrder).filter(RegistrationOrder.id == registration_order.id).update({
        RegistrationOrder.event_id: registration_order.event_id,
        RegistrationOrder.attendee_id: registration_order.attendee_id,
        RegistrationOrder.amount: registration_order.amount,
        RegistrationOrder.tax_amount: registration_order.tax_amount,
        RegistrationOrder.fee_amount: registration_order.fee_amount,
        RegistrationOrder.total_amount: registration_order.amount + registration_order.tax_amount + registration_order.fee_amount,
        RegistrationOrder.updated_on: datetime.now()
    })
    db.commit()
    return db.query(RegistrationOrder).filter(RegistrationOrder.id == registration_order.id).first()

def update_registration_order_temp(db: Session, registration_order: RegistrationOrder):
    db.query(RegistrationOrder).filter(RegistrationOrder.id == registration_order.id).update({
        RegistrationOrder.event_id: registration_order.event_id,
        RegistrationOrder.attendee_id: registration_order.attendee_id,
        RegistrationOrder.amount: registration_order.amount,
        RegistrationOrder.tax_amount: registration_order.tax_amount,
        RegistrationOrder.fee_amount: registration_order.fee_amount,
        RegistrationOrder.total_amount: registration_order.amount + registration_order.tax_amount + registration_order.fee_amount,
        RegistrationOrder.updated_on: datetime.now()
    })
    db.commit()
    return db.query(RegistrationOrder).filter(RegistrationOrder.id == registration_order.id).first()

def delete_registration_order(db: Session, uuid: str):
    registration_order = get_registration_order_by_uuid(db, uuid)
    if registration_order is None:
        raise HTTPException(status_code=Status.HTTP_404_NOT_FOUND, detail="Registration order not found")
    db.query(RegistrationOrderItem).filter(RegistrationOrderItem.registration_order_id == registration_order.id).delete()
    db.delete(registration_order)
    db.commit()
    return registration_order