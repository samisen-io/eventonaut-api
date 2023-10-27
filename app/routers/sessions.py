from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.oauth2 import get_current_active_user
from ..schemas import session_schemas as schemas
from ..schemas import user_schemas as uschemas
from ..crud import sessions_crud as crud, conferences_crud
from ..dependencies import get_db
from datetime import date, time

router = APIRouter(tags=["sessions"])

# create session by owner id and conference id
@router.post("/sessions", response_model=schemas.Session)
def create_session_for_conference(
    session: schemas.SessionCreate, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)
):
    if session.conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference id")
    conference=conferences_crud.get_conference_by_owner_id(db, conference_id=session.conference_id, owner_id=current_user.id)
    if conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    if session.date < conference.start_date or session.date > conference.end_date or session.date < date.today():
        raise HTTPException(status_code=400, detail="Invalid date")
    if session.start_time > session.end_time:
        raise HTTPException(status_code=400, detail="Invalid time")
    return crud.create_conference_session(db=db, session=session, owner_id=current_user.id)

# get all sessions
@router.get("/sessions/all_sesssions", response_model=list[schemas.Session])
def get_all_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sessions = crud.get_sessions(db, skip=skip, limit=limit)
    if sessions is None or len(sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions

# get all sessions by conference id
@router.get("/sessions/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_conference_id(conference_id: int, db: Session = Depends(get_db)):
    if conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid session id")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_sessions = crud.get_all_sessions_by_conference_id(db, conference_id=conference_id)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

# get all conferences based to name or description of the session
@router.get("/sessions/{conference_id}/search/{search}", response_model=list[schemas.Session])
def get_sessions_by_search(conference_id: int, search: str, db: Session = Depends(get_db)):
    if conference_id <= 0 or search.isnumeric():
        raise HTTPException(status_code=400, detail="Invalid conference id or search")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_sessions = crud.get_all_sessions_by_search(db,conference_id=conference_id, search_string=search)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="No sessions found for conference")
    return db_sessions

# get all sessions by conference id and between dates range
@router.get("/sessions/{conference_id}/filter_start_date/{filter_start_date}/filter_end_date/{filter_end_date}", response_model=list[schemas.Session])
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
@router.put("/sessions", response_model=schemas.Session)
def update_session(session: schemas.SessionUpdate, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)):
    if session.id <= 0 or session.conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid session id or conference id")
    if conferences_crud.get_conference_by_owner_id(db, conference_id=session.conference_id,owner_id=current_user.id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_session = crud.get_session_by_owner_id(db, session_id=session.id, owner_id=current_user.id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    conference=conferences_crud.get_conference_by_owner_id(db, conference_id=db_session.conference_id, owner_id=current_user.id)
    if session.date < conference.start_date or session.date > conference.end_date or session.date < date.today():
        raise HTTPException(status_code=400, detail="Invalid date")
    if session.start_time > session.end_time:
        raise HTTPException(status_code=400, detail="Invalid time")
    return crud.update_session(db=db, session=session, session_id=session.id, owner_id=current_user.id)

#delete session
@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)):
    if session_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid session id")
    db_session = crud.get_session_by_owner_id(db, session_id=session_id, owner_id=current_user.id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return crud.delete_session(db=db, session_id=session_id, owner_id=current_user.id)