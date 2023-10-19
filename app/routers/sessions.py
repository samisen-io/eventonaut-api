from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import schemas
from ..crud import sessions_crud as crud, conferences_crud
from ..dependencies import get_db
from datetime import date, time

router = APIRouter(tags=["sessions"])

# create session by owner id and conference id
@router.post("/sessions/conference_id/{conference_id}", response_model=schemas.Session)
def create_session_for_conference(
    conference_id: int, session: schemas.SessionCreate, db: Session = Depends(get_db)
):
    if conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference id")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return crud.create_conference_session(db=db, session=session, conference_id=conference_id)

# get all sessions
@router.get("/sessions/", response_model=list[schemas.Session])
def get_all_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sessions = crud.get_sessions(db, skip=skip, limit=limit)
    if sessions is None or len(sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions

# get session by id
@router.get("/sessions/session_id/{session_id}", response_model=schemas.Session)
def get_session_by_session_id(session_id: int, db: Session = Depends(get_db)):
    if session_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid session id")
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

# get sessions by name
@router.get("/sessions/conference_id/{conference_id}/name/{name}", response_model=list[schemas.Session])
def get_all_sessions_by_name(conference_id:int, name: str, db: Session = Depends(get_db)):
    if name.isnumeric() or conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid name or session id")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_session = crud.get_sessions_by_name(db,conference_id=conference_id, name=name)
    if db_session is None or len(db_session) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

# get all sessions by start_time
@router.get("/sessions/conference_id/{conference_id}/start_time/{start_time}", response_model=list[schemas.Session])
def get_all_sessions_by_start_time(conference_id: int, start_time: time, db: Session = Depends(get_db)):
    if conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid session id")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_sessions = crud.get_sessions_by_start_time(db,conference_id=conference_id, start_time=start_time)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

# get all sessions by end_time
@router.get("/sessions/conference_id/{conference_id}/end_time/{end_time}", response_model=list[schemas.Session])
def get_all_sessions_by_end_time(conference_id: int, end_time: time, db: Session = Depends(get_db)):
    if conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid session id")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_sessions = crud.get_sessions_by_end_time(db,conference_id=conference_id, end_time=end_time)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

# get all sessions by date
@router.get("/sessions/conference_id/{conference_id}/date/{date}", response_model=list[schemas.Session])
def get_sessions_by_date(conference_id: int, date: date, db: Session = Depends(get_db)):
    if conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid session id")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_sessions = crud.get_sessions_by_date(db, conference_id=conference_id, date=date)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

# get all sessions by description
@router.get("/sessions/conference_id/{conference_id}/description/{description}", response_model=list[schemas.Session])
def get_sessions_by_description(conference_id: int, description: str, db: Session = Depends(get_db)):
    if conference_id <= 0 or description.isnumeric():
        raise HTTPException(status_code=400, detail="Invalid session id or description")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_sessions = crud.get_sessions_by_description(db,conference_id=conference_id, description=description)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

# get all sessions by location
@router.get("/sessions/conference_id/{conference_id}/location/{location}", response_model=list[schemas.Session])
def get_sessions_by_location(conference_id:int, location: str, db: Session = Depends(get_db)):
    if conference_id <= 0 or location.isnumeric():
        raise HTTPException(status_code=400, detail="Invalid session id or location")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_sessions = crud.get_sessions_by_location(db,conference_id=conference_id, location=location)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

# get all sessions by conference id
@router.get("/sessions/conference_id/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_conference_id(conference_id: int, db: Session = Depends(get_db)):
    if conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid session id")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_sessions = crud.get_all_sessions_by_conference_id(db, conference_id=conference_id)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

# get all sessions by conference id and between dates range
@router.get("/sessions/conference_id/{conference_id}/filter_start_date/{filter_start_date}/filter_end_date/{filter_end_date}", response_model=list[schemas.Session])
def get_all_sessions_by_conference_id_and_between_dates(conference_id: int, filter_start_date: date, filter_end_date: date, db: Session = Depends(get_db)):
    if conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid session id")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    if filter_start_date > filter_end_date:
        raise HTTPException(status_code=400, detail="Invalid date range")
    db_sessions = crud.get_all_sessions_by_conference_id_between_date(db, conference_id=conference_id, filter_start_date=filter_start_date, filter_end_date=filter_end_date)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

# update session
@router.put("/sessions/{session_id}", response_model=schemas.Session)
def update_session(session_id: int, session: schemas.SessionCreate, db: Session = Depends(get_db)):
    if session_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid session id")
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return crud.update_session(db=db, session=session, session_id=session_id)

#delete session
@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    if session_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid session id")
    db_session = crud.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return crud.delete_session(db=db, session_id=session_id)

#delete all sessions by conference id
@router.delete("/sessions/conference_id/{conference_id}")
def delete_sessions_by_conference_id(conference_id: int, db: Session = Depends(get_db)):
    if conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_sessions = crud.get_all_sessions_by_conference_id(db, conference_id=conference_id)
    if not db_sessions or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="No sessions found for conference")
    crud.delete_all_sessions_by_conference_id(db=db, conference_id=conference_id)
    return {"message": "Sessions deleted successfully"}