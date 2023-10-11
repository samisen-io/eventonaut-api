from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..dependencies import get_db

router = APIRouter()

#session crud
@router.post("/sessions/", response_model=schemas.Session)
def create_session_for_conference(
    conference_id: int, session: schemas.SessionCreate, db: Session = Depends(get_db)
):
    return crud.create_conference_session(db=db, session=session, conference_id=conference_id)

@router.get("/sessions/", response_model=list[schemas.Session])
def read_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sessions = crud.get_sessions(db, skip=skip, limit=limit)
    return sessions

@router.get("/sessions/{session_id}", response_model=schemas.Session)
def read_session(session_id: int, db: Session = Depends(get_db)):
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

@router.get("/sessions/name/{name}", response_model=schemas.Session)
def read_session_by_name(name: str, db: Session = Depends(get_db)):
    db_session = crud.get_session_by_name(db, name=name)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

#get sessions by start_time
@router.get("/sessions/start_time/{start_time}", response_model=list[schemas.Session])
def get_sessions_by_start_time(start_time: str, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_start_time(db, start_time=start_time)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by end_time
@router.get("/sessions/end_time/{end_time}", response_model=list[schemas.Session])
def get_sessions_by_end_time(end_time: str, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_end_time(db, end_time=end_time)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by date
@router.get("/sessions/date/{date}", response_model=list[schemas.Session])
def get_sessions_by_date(date: str, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_date(db, date=date)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by description
@router.get("/sessions/description/{description}", response_model=list[schemas.Session])
def get_sessions_by_description(description: str, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_description(db, description=description)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by location
@router.get("/sessions/location/{location}", response_model=list[schemas.Session])
def get_sessions_by_location(location: str, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_location(db, location=location)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by date by conference_id
@router.get("/sessions/date/{date}/conference/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_date_conference_id(date: str, conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_date_conference_id(db, date=date, conference_id=conference_id)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by start_time by conference_id
@router.get("/sessions/start_time/{start_time}/conference/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_start_time_conference_id(start_time: str, conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_start_time_conference_id(db, start_time=start_time, conference_id=conference_id)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by end_time by conference_id
@router.get("/sessions/end_time/{end_time}/conference/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_end_time_conference_id(end_time: str, conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_end_time_conference_id(db, end_time=end_time, conference_id=conference_id)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by location by conference_id
@router.get("/sessions/location/{location}/conference/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_location_conference_id(location: str, conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_location_conference_id(db, location=location, conference_id=conference_id)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by description by conference_id
@router.get("/sessions/description/{description}/conference/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_description_conference_id(description: str, conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_description_conference_id(db, description=description, conference_id=conference_id)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#get sessions by conference id
@router.get("/sessions/conference/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_conference_id(conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_conference_id(db, conference_id=conference_id)
    if db_sessions is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

#update session
@router.put("/sessions/{session_id}", response_model=schemas.Session)
def update_session(session_id: int, session: schemas.SessionCreate, db: Session = Depends(get_db)):
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return crud.update_session(db=db, session=session, session_id=session_id)

#delete session
@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return crud.delete_session(db=db, session_id=session_id)

#delete all sessions by conference id
@router.delete("/sessions/conference/{conference_id}")
def delete_sessions_by_conference(conference_id: int, db: Session = Depends(get_db)):
    db_sessions = crud.get_sessions_by_conference_id(db, conference_id=conference_id)
    if not db_sessions:
        raise HTTPException(status_code=404, detail="No sessions found for conference")
    for session in db_sessions:
        crud.delete_session(db=db, session_id=session.id)
    return {"message": "Sessions deleted successfully"}
