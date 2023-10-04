import shutil
import tempfile
from fastapi import Depends, FastAPI, File, HTTPException, Path, UploadFile
from sqlalchemy.orm import Session

from data_ingester import ingest_file

from . import crud, models, schemas
from .database import SessionLocal, engine

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#function to upload file that needs to saved in a folder called "uploads" with a random suffix
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = tempfile.NamedTemporaryFile(suffix=suffix, dir=temp_dir)
        shutil.copyfileobj(file.file, temp_file)
        ingest_file(temp_file.name)
        return {"filename": file.filename}

#function to get user
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#function to get all users
@app.get("/users/", response_model=schemas.User)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

#function to create user
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

#function to delete user
@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db=db, user_id=user_id)
    return db_user

#function to get conference
@app.get("/conferences/{conference_id}", response_model=schemas.Conference)
def read_conference(conference_id: int, db: Session = Depends(get_db)):
    db_conference = crud.get_conference(db, conference_id=conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference

#function to get all conferences
@app.get("/conferences/", response_model=schemas.Conference)
def read_conferences(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    conferences = crud.get_conferences(db, skip=skip, limit=limit)
    return conferences

#function to create conference
@app.post("/conferences/", response_model=schemas.Conference)
def create_conference(conference: schemas.ConferenceCreate, db: Session = Depends(get_db)):
    return crud.create_conference(db=db, conference=conference)

#function to delete conference
@app.delete("/conferences/{conference_id}", response_model=schemas.Conference)
def delete_conference(conference_id: int, db: Session = Depends(get_db)):
    db_conference = crud.delete_conference(db=db, conference_id=conference_id)
    return db_conference

@app.get("/")
async def root():
    return {"message": "Hello World"}
