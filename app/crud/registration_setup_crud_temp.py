from datetime import datetime
import uuid

from app.schemas.registration_setup_schema_temp import RegistrationSetupCreateTemp
from ..import models
from sqlalchemy.orm import Session, joinedload

def create_registration_setup(db: Session, registration_setup: RegistrationSetupCreateTemp):
    db_registration_setup = models.RegistrationSetup(
        uuid = 'reg-'+str(uuid.uuid4()),
        event_id = registration_setup.event_id,
        end_date = registration_setup.end_date,
        registration_note = registration_setup.registration_note,
        tax_name = registration_setup.tax_name,
        tax_rate = registration_setup.tax_rate/100,
        fee_name = registration_setup.fee_name,
        fee_amount = registration_setup.fee_amount/100,
        refund_policy = registration_setup.refund_policy,
        is_live = registration_setup.is_live,
        start_date = registration_setup.start_date,
        created_on = datetime.now(),
        updated_on = datetime.now()
    )
    db.add(db_registration_setup)
    db.commit()
    db.refresh(db_registration_setup)
    return db_registration_setup

def get_registration_setup(db: Session, registration_setup_id: int):
    return db.query(models.RegistrationSetup).filter(models.RegistrationSetup.id == registration_setup_id).first()

def get_registration_setup_by_uuid(db: Session, registration_setup_uuid: str):
    return db.query(models.RegistrationSetup).filter(models.RegistrationSetup.uuid == registration_setup_uuid).first()

def get_registration_setup_by_event_id(db: Session, event_id: int):
    return db.query(models.RegistrationSetup).filter(models.RegistrationSetup.event_id == event_id).first()