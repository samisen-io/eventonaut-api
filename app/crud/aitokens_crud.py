from sqlalchemy.orm import Session
from .. import models
from ..schemas import aitokens_schemas as schemas
from datetime import datetime
import uuid

def insert_aitoken(db: Session, aitoken: schemas.AITokensCreate):
    db_aitoken = models.AITokens()
    db_aitoken.conference_id = db.query(models.Conference).filter(models.Conference.uuid == aitoken.conference_id).first().id
    user = db.query(models.User).filter(models.User.uuid == aitoken.attendee_id).first()
    db_aitoken.attendee_id = db.query(models.Attendee).filter(models.Attendee.user_id == user.id).first().id
    db_aitoken.successful_requests = aitoken.successful_requests
    db_aitoken.total_cost = aitoken.total_cost
    db_aitoken.total_tokens = aitoken.total_tokens
    db_aitoken.prompt_tokens = aitoken.prompt_tokens
    db_aitoken.completion_tokens = aitoken.completion_tokens
    db_aitoken.processing_time = aitoken.processing_time
    db_aitoken.created_on = datetime.utcnow()
    db_aitoken.updated_on = datetime.utcnow()
    db_aitoken.uuid = str(uuid.uuid4())
    db.add(db_aitoken)
    db.commit()
    db.refresh(db_aitoken)
    return db_aitoken

def get_aitoken(db: Session, aitoken_id: str):
    return db.query(models.AITokens).filter(models.AITokens.uuid == aitoken_id).first()

def get_aitokens(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.AITokens).offset(skip).limit(limit).all()

def delete_aitoken(db: Session, aitoken_id: str):
    db.query(models.AITokens).filter(models.AITokens.uuid == aitoken_id).delete()
    db.commit()
    return True