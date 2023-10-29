from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.oauth2 import get_current_active_user
from ..schemas import session_schemas as schemas
from ..schemas import user_schemas as uschemas
from ..crud import sessions_crud as crud, conferences_crud
from ..dependencies import get_db
from ..encryption import encrypt_number, decrypt_number
from datetime import date

router = APIRouter(tags=["sessions"])

# create session by owner id and conference id
@router.post("/sessions", response_model=schemas.Session)
def create_session_for_conference(
    session: schemas.SessionCreate, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)
):
    try:
        conference_id = decrypt_number(session.conference_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conference id")
    conference=conferences_crud.get_conference_by_owner_id(db, conference_id=conference_id, owner_id=current_user.id)
    if conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    if session.date < conference.start_date or session.date > conference.end_date or session.date < date.today():
        raise HTTPException(status_code=400, detail="Invalid date")
    if session.start_time > session.end_time:
        raise HTTPException(status_code=400, detail="Invalid time")
    session=crud.create_conference_session(db=db, session=session, owner_id=current_user.id)
    session.conference_id=encrypt_number(session.conference_id).decode()
    session.owner_id=encrypt_number(session.owner_id).decode()
    session.id=encrypt_number(session.id).decode()
    return session

# get all sessions
@router.get("/sessions/all_sessions")
def get_all_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if skip < 0 or limit < 0:
        raise HTTPException(status_code=400, detail="Invalid query parameters")
    db_sessions = crud.get_sessions(db, skip=skip, limit=limit)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    for session in db_sessions:
        session.conference_id=encrypt_number(session.conference_id)
        session.owner_id=encrypt_number(session.owner_id)
        session.id=encrypt_number(session.id)
    return db_sessions

# get all sessions by conference id
@router.get("/sessions/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_conference_id(conference_id: str, db: Session = Depends(get_db)):
    try:
        conference_id:int = decrypt_number(conference_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conference id")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_sessions = crud.get_all_sessions_by_conference_id(db, conference_id=conference_id)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    for session in db_sessions:
        session.conference_id=encrypt_number(session.conference_id)
        session.owner_id=encrypt_number(session.owner_id)
        session.id=encrypt_number(session.id)
    return db_sessions

# get all conferences based to name or description of the session
@router.get("/sessions/{conference_id}/search/{search}", response_model=list[schemas.Session])
def get_sessions_by_search(conference_id: str, search: str, db: Session = Depends(get_db)):
    try:
        conference_id = decrypt_number(conference_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conference id")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_sessions = crud.get_all_sessions_by_search(db,conference_id=conference_id, search_string=search)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="No sessions found for conference")
    for session in db_sessions:
        session.conference_id=encrypt_number(session.conference_id)
        session.owner_id=encrypt_number(session.owner_id)
        session.id=encrypt_number(session.id)
    return db_sessions

# get all sessions by conference id and between dates range
@router.get("/sessions/{conference_id}/filter_start_date/{filter_start_date}/filter_end_date/{filter_end_date}", response_model=list[schemas.Session])
def get_all_sessions_by_conference_id_and_between_dates(conference_id: str, filter_start_date: date, filter_end_date: date, db: Session = Depends(get_db)):
    try:
        conference_id = decrypt_number(conference_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conference id")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    if filter_start_date > filter_end_date:
        raise HTTPException(status_code=400, detail="Invalid date range")
    db_sessions = crud.get_all_sessions_by_conference_id_between_date(db, conference_id=conference_id, filter_start_date=filter_start_date, filter_end_date=filter_end_date)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    for session in db_sessions:
        session.conference_id=encrypt_number(session.conference_id)
        session.owner_id=encrypt_number(session.owner_id)
        session.id=encrypt_number(session.id)
    return db_sessions

# update session
@router.put("/sessions", response_model=schemas.Session)
def update_session(session: schemas.SessionUpdate, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)):
    try:
        session.id = decrypt_number(session.id)
    except:
        raise HTTPException(status_code=400, detail="Invalid session id")
    try:
        conference_id = decrypt_number(session.conference_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid conference id")
    if conferences_crud.get_conference_by_owner_id(db, conference_id=conference_id,owner_id=current_user.id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_session = crud.get_session_by_owner_id(db, session_id=session.id, owner_id=current_user.id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    conference=conferences_crud.get_conference_by_owner_id(db, conference_id=conference_id, owner_id=current_user.id)
    if session.date < conference.start_date or session.date > conference.end_date or session.date < date.today():
        raise HTTPException(status_code=400, detail="Invalid date")
    if session.start_time > session.end_time:
        raise HTTPException(status_code=400, detail="Invalid time")
    session=crud.update_session(db=db, session=session, session_id=session.id, owner_id=current_user.id)
    session.conference_id=encrypt_number(session.conference_id)
    session.owner_id=encrypt_number(session.owner_id)
    session.id=encrypt_number(session.id)
    return session

#delete session
@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)):
    try:
        session_id = decrypt_number(session_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid session id")
    db_session = crud.get_session_by_owner_id(db, session_id=session_id, owner_id=current_user.id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return crud.delete_session(db=db, session_id=session_id, owner_id=current_user.id)