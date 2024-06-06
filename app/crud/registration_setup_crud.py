from ..import models
from sqlalchemy.orm import Session, joinedload

def get_setup_details(db: Session, event_id: int):
    return db.query(models.RegistrationSetup).options(joinedload(models.RegistrationSetup.registration_setup_items)).filter(models.RegistrationSetup.event_id == event_id).first()