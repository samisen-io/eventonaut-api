from .database import SessionLocal, engine
from . import models
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

