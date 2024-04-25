from fastapi import HTTPException
from .database import SessionLocal, engine
from . import models
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    except HTTPException as e:
        raise e
    finally:
        db.close()

