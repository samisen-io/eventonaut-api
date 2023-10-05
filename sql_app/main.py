from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#conference crud
@app.post("/conferences/", response_model=schemas.Conference)
def create_conference_for_user(
    user_id: int, conference: schemas.ConferenceCreate, db: Session = Depends(get_db)
):
    return crud.create_user_conference(db=db, conference=conference, user_id=user_id)

@app.get("/conferences/", response_model=list[schemas.Conference])
def read_conferences(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    conferences = crud.get_conferences(db, skip=skip, limit=limit)
    return conferences

@app.get("/conferences/{conference_id}", response_model=schemas.Conference)
def read_conference(conference_id: int, db: Session = Depends(get_db)):
    db_conference = crud.get_conference(db, conference_id=conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference

@app.get("/conferences/name/{name}", response_model=schemas.Conference)
def read_conference_by_name(name: str, db: Session = Depends(get_db)):
    db_conference = crud.get_conference_by_name(db, name=name)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference

#get conference by location
@app.get("/conferences/location/{location}", response_model=schemas.Conference)
def read_conference_by_location(location: str, db: Session = Depends(get_db)):
    db_conference = crud.get_conference_by_location(db, location=location)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference

#get conference by start_date
@app.get("/conferences/start_date/{start_date}", response_model=schemas.Conference)
def read_conference_by_start_date(start_date: str, db: Session = Depends(get_db)):
    db_conference = crud.get_conference_by_start_date(db, start_date=start_date)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference

#get conference by end_date
@app.get("/conferences/end_date/{end_date}", response_model=schemas.Conference)
def read_conference_by_end_date(end_date: str, db: Session = Depends(get_db)):
    db_conference = crud.get_conference_by_end_date(db, end_date=end_date)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference

#get conference by description
@app.get("/conferences/description/{description}", response_model=schemas.Conference)
def read_conference_by_description(description: str, db: Session = Depends(get_db)):
    db_conference = crud.get_conference_by_description(db, description=description)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference

#get all conferences by owner_id
@app.get("/conferences/owner/{owner_id}", response_model=list[schemas.Conference])
def read_conferences_by_owner_id(owner_id: int, db: Session = Depends(get_db)):
    db_conferences = crud.get_conferences_by_owner_id(db, owner_id=owner_id)
    if db_conferences is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

#update conference
@app.put("/conferences/{conference_id}", response_model=schemas.Conference)
def update_conference(conference_id: int, conference: schemas.ConferenceCreate, db: Session = Depends(get_db)):
    db_conference = crud.get_conference(db, conference_id=conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return crud.update_conference(db=db, conference=conference, conference_id=conference_id)

#delete conference
@app.delete("/conferences/{conference_id}")
def delete_conference(conference_id: int, db: Session = Depends(get_db)):
    db_conference = crud.get_conference(db, conference_id=conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return crud.delete_conference(db=db, conference_id=conference_id)

# delete all conferences by owner id
@app.delete("/conferences/owner/{owner_id}")
def delete_conferences_by_owner(owner_id: int, db: Session = Depends(get_db)):
    db_conferences = crud.get_conferences_by_owner_id(db, owner_id=owner_id)
    if not db_conferences:
        raise HTTPException(status_code=404, detail="No conferences found for owner")
    for conference in db_conferences:
        crud.delete_conference(db=db, conference_id=conference.id)
    return {"message": "Conferences deleted successfully"}