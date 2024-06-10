from datetime import datetime
from sqlalchemy.orm import Session
import uuid
import logging

from app.models import RegistrationOrderItemType

def get_registration_order_item_type_by_id(db: Session, id: int):
    return db.query(RegistrationOrderItemType).filter(RegistrationOrderItemType.id == id).first()

def get_registration_order_item_type_by_code(db: Session, code: str):
    return db.query(RegistrationOrderItemType).filter(RegistrationOrderItemType.code == code).first()