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

#update user
@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.update_user(db=db, user=user, user_id=user_id)

#delete user
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.delete_user(db=db, user_id=user_id)

#get user by account_type
@app.get("/users/account_type/{account_type}", response_model=list[schemas.User])
def read_user_by_account_type(account_type: str, db: Session = Depends(get_db)):
    db_user = crud.get_users_by_account_type(db, account_type=account_type)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

#get user by bussiness_type
@app.get("/users/bussiness_type/{bussiness_type}", response_model=list[schemas.User])
def read_user_by_bussiness_type(bussiness_type: str, db: Session = Depends(get_db)):
    db_user = crud.get_users_by_bussiness_type(db, bussiness_type=bussiness_type)
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

#get conferences by start_date
@app.get("/conferences/start_date/{start_date}", response_model=list[schemas.Conference])
def read_conferences_by_start_date(start_date: str, db: Session = Depends(get_db)):
    db_conferences = crud.get_conferences_by_start_date(db, start_date=start_date)
    if db_conferences is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

#get conferences by end_date
@app.get("/conferences/end_date/{end_date}", response_model=list[schemas.Conference])
def read_conferences_by_end_date(end_date: str, db: Session = Depends(get_db)):
    db_conferences = crud.get_conferences_by_end_date(db, end_date=end_date)
    if db_conferences is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

#get conference by description
@app.get("/conferences/description/{description}", response_model=schemas.Conference)
def read_conference_by_description(description: str, db: Session = Depends(get_db)):
    db_conference = crud.get_conference_by_description(db, description=description)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference

#get conferences by name by owner_id
@app.get("/conferences/name/{name}/owner/{owner_id}", response_model=schemas.Conference)
def read_conferences_by_name_owner_id(name: str, owner_id: int, db: Session = Depends(get_db)):
    db_conferences = crud.get_conferences_by_name_owner_id(db, name=name, owner_id=owner_id)
    if db_conferences is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

#get conferences by location by owner_id
@app.get("/conferences/location/{location}/owner/{owner_id}", response_model=schemas.Conference)
def read_conferences_by_location_owner_id(location: str, owner_id: int, db: Session = Depends(get_db)):
    db_conferences = crud.get_conferences_by_location_owner_id(db, location=location, owner_id=owner_id)
    if db_conferences is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

#get conferences by start_date by owner_id
@app.get("/conferences/start_date/{start_date}/owner/{owner_id}", response_model=list[schemas.Conference])
def read_conferences_by_start_date_owner_id(start_date: str, owner_id: int, db: Session = Depends(get_db)):
    db_conferences = crud.get_conferences_by_start_date_owner_id(db, start_date=start_date, owner_id=owner_id)
    if db_conferences is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

#get conferences by end_date by owner_id
@app.get("/conferences/end_date/{end_date}/owner/{owner_id}", response_model=list[schemas.Conference])
def read_conferences_by_end_date_owner_id(end_date: str, owner_id: int, db: Session = Depends(get_db)):
    db_conferences = crud.get_conferences_by_end_date_owner_id(db, end_date=end_date, owner_id=owner_id)
    if db_conferences is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

#get conferences by description by owner_id
@app.get("/conferences/description/{description}/owner/{owner_id}", response_model=schemas.Conference)
def read_conferences_by_description_owner_id(description: str, owner_id: int, db: Session = Depends(get_db)):
    db_conferences = crud.get_conferences_by_description_owner_id(db, description=description, owner_id=owner_id)
    if db_conferences is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

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

#session crud
@app.post("/sessions/", response_model=schemas.Session)
def create_session_for_conference(
    conference_id: int, session: schemas.SessionCreate, db: Session = Depends(get_db)
):
    return crud.create_conference_session(db=db, session=session, conference_id=conference_id)

@app.get("/sessions/", response_model=list[schemas.Session])
def read_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sessions = crud.get_sessions(db, skip=skip, limit=limit)
    return sessions

@app.get("/sessions/{session_id}", response_model=schemas.Session)
def read_session(session_id: int, db: Session = Depends(get_db)):
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

@app.get("/sessions/name/{name}", response_model=schemas.Session)
def read_session_by_name(name: str, db: Session = Depends(get_db)):
    db_session = crud.get_session_by_name(db, name=name)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

#get sessions by start_time
@app.get("/sessions/start_time/{start_time}", response_model=list[schemas.Session])
def get_sessions_by_start_time(start_time: str, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_start_time(db, start_time=start_time)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by end_time
@app.get("/sessions/end_time/{end_time}", response_model=list[schemas.Session])
def get_sessions_by_end_time(end_time: str, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_end_time(db, end_time=end_time)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by date
@app.get("/sessions/date/{date}", response_model=list[schemas.Session])
def get_sessions_by_date(date: str, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_date(db, date=date)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by description
@app.get("/sessions/description/{description}", response_model=list[schemas.Session])
def get_sessions_by_description(description: str, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_description(db, description=description)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by location
@app.get("/sessions/location/{location}", response_model=list[schemas.Session])
def get_sessions_by_location(location: str, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_location(db, location=location)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by date by conference_id
@app.get("/sessions/date/{date}/conference/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_date_conference_id(date: str, conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_date_conference_id(db, date=date, conference_id=conference_id)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by start_time by conference_id
@app.get("/sessions/start_time/{start_time}/conference/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_start_time_conference_id(start_time: str, conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_start_time_conference_id(db, start_time=start_time, conference_id=conference_id)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by end_time by conference_id
@app.get("/sessions/end_time/{end_time}/conference/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_end_time_conference_id(end_time: str, conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_end_time_conference_id(db, end_time=end_time, conference_id=conference_id)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by location by conference_id
@app.get("/sessions/location/{location}/conference/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_location_conference_id(location: str, conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_location_conference_id(db, location=location, conference_id=conference_id)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by description by conference_id
@app.get("/sessions/description/{description}/conference/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_description_conference_id(description: str, conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_description_conference_id(db, description=description, conference_id=conference_id)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by conference id
@app.get("/sessions/conference/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_conference_id(conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_conference_id(db, conference_id=conference_id)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#update session
@app.put("/sessions/{session_id}", response_model=schemas.Session)
def update_session(session_id: int, session: schemas.SessionCreate, db: Session = Depends(get_db)):
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return crud.update_session(db=db, session=session, session_id=session_id)

#delete session
@app.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return crud.delete_session(db=db, session_id=session_id)

#delete all sessions by conference id
@app.delete("/sessions/conference/{conference_id}")
def delete_sessions_by_conference(conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_conference_id(db, conference_id=conference_id)
    if not db_sessions:
        raise HTTPException(status_code=404, detail="No sessions found for conference")
    for session in db_sessions:
        crud.delete_session(db=db, session_id=session.id)
    return {"message": "Sessions deleted successfully"}
