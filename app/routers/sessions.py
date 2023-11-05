from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.oauth2 import get_current_active_user
from ..schemas import session_schemas as schemas
from ..schemas import user_schemas as uschemas
from ..crud import sessions_crud as crud, conferences_crud
from ..dependencies import get_db
from datetime import date

router = APIRouter(tags=["sessions"])

# create session by owner id and conference id
@router.post("/sessions", response_model=schemas.Session)
def create_session_for_conference(
    session: schemas.SessionCreate, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)
):
    conference=conferences_crud.get_conference_by_uuid(db, uuid=session.conference_id, owner_id=current_user.id)
    if conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    if session.date < conference.start_date or session.date > conference.end_date or session.date < date.today():
        raise HTTPException(status_code=400, detail=f"Invalid date! The valid range for this Conference is: {conference.start_date} - {conference.end_date}")
    if session.start_time > session.end_time:
        raise HTTPException(status_code=400, detail="Invalid time")
    return crud.create_conference_session(db=db, session=session, owner_id=current_user.id)

# get all sessions
@router.get("/sessions/all_sessions", response_model=list[schemas.Session])
def get_all_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if skip < 0 or limit < 0:
        raise HTTPException(status_code=400, detail="Invalid query parameters")
    db_sessions = crud.get_sessions(db, skip=skip, limit=limit)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

# get all sessions by conference id
@router.get("/sessions/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_conference_id(conference_id: str, db: Session = Depends(get_db)):
    if conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_sessions = crud.get_all_sessions_by_uuid_id(db, conference_uuid=conference_id)
    if db_sessions is None or len(db_sessions) == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_sessions

# update session
@router.put("/sessions")
def update_session(session: schemas.SessionUpdate, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)):
    if conferences_crud.get_conference_by_uuid(db, uuid=session.conference_id,owner_id=current_user.id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    db_session = crud.get_session_by_uuid_id(db, uuid=session.id, owner_id=current_user.id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    conference=conferences_crud.get_conference_by_uuid_id(db, uuid=session.conference_id, owner_id=current_user.id)
    if session.date < conference.start_date or session.date > conference.end_date or session.date < date.today():
        raise HTTPException(status_code=400, detail="Invalid date")
    if session.start_time > session.end_time:
        raise HTTPException(status_code=400, detail="Invalid time")
    return crud.update_session(db=db, session=session, uuid=session.id, owner_id=current_user.id)

#delete session
@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db), current_user: uschemas.User = Depends(get_current_active_user)):
    db_session = crud.get_session_by_uuid_id(db, uuid=session_id, owner_id=current_user.id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return crud.delete_session(db=db, uuid=session_id, owner_id=current_user.id)