from app.schemas.registration_setup_schemas import RegistrationSetupItem
from ..import models
from sqlalchemy.orm import Session, joinedload

def get_registration_setup_item(db: Session, registration_setup_item_id: int):
    return db.query(models.RegistrationSetupItem).filter(models.RegistrationSetupItem.id == registration_setup_item_id).first()