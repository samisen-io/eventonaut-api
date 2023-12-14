from sqlalchemy.orm import Session
from .. import models
from datetime import datetime
import uuid
from apscheduler.schedulers.background import BackgroundScheduler
from ..database import SessionLocal

def insert_token(db: Session, token_jti: str, expire_time: datetime, is_invalidated: bool):
    token = db.query(models.LogoutToken).filter(models.LogoutToken.token_jti == token_jti).first()
    
    if token is None:
        token = models.LogoutToken(uuid=str(uuid.uuid4()), token_jti=token_jti, created_on=datetime.utcnow())
        token.updated_on = datetime.utcnow()
        db.add(token)
    else:
        token.updated_on = datetime.utcnow()

    token.expires_on = expire_time
    token.is_invalidated = is_invalidated

    db.commit()
    db.refresh(token)
    return token

def get_all_jti_in_tokens(db: Session):
    return [token.token_jti for token in db.query(models.LogoutToken).all()]

def delete_data():
    db = SessionLocal()
    try:
        item = db.query(models.LogoutToken).filter(models.LogoutToken.expires_on < datetime.now()).all()
        for i in item:
            db.delete(i)
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(delete_data, 'interval', minutes=60)
    scheduler.start()