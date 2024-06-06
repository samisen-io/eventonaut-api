from sqlalchemy.orm import Session
from ..models import MasterTemplate
import uuid
from datetime import datetime

def insert_master_template(db: Session, template_name: str, template_url: str):
    db_template = MasterTemplate()
    db_template.uuid = 'tem-' + str(uuid.uuid4())
    db_template.created_on = db_template.updated_on = datetime.utcnow()
    db_template.template_name = template_name
    db_template.template_url = template_url
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def get_master_templates(db: Session):
    return db.query(MasterTemplate).all()

def get_master_template_by_id(db: Session, template_id: str):
    return db.query(MasterTemplate).filter(MasterTemplate.uuid == template_id).first()

def delete_master_template(db: Session, template: MasterTemplate):
    db.delete(template)
    db.commit()
    return True