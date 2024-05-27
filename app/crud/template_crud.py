from sqlalchemy.orm import Session
from ..models import Template
import uuid
from datetime import datetime

def insert_template(db: Session, template_name: str, template_url: str, organization_id: int):
    db_template = Template()
    db_template.uuid = 'tem-' + str(uuid.uuid4())
    db_template.created_on = db_template.updated_on = datetime.utcnow()
    db_template.template_name = template_name
    db_template.template_url = template_url
    db_template.organization_id = organization_id
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def get_templates(db: Session, organization_id: int):
    return db.query(Template).filter(Template.organization_id == organization_id).all()

def get_template_by_id(db: Session, template_id: str, organization_id: int):
    return db.query(Template).filter(Template.uuid == template_id, Template.organization_id == organization_id).first()

def delete_template(db: Session, template: Template):
    db.delete(template)
    db.commit()
    return True