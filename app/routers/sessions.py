from fastapi import APIRouter, HTTPException, Depends, Security
import logging
from sqlalchemy.orm import Session
from app.schemas.user_schemas import UserAuthentication as User
from app.oauth2 import get_current_active_user
from ..schemas import session_schemas as schemas
from ..crud import sessions_crud as crud, conferences_crud
from ..dependencies import get_db
from .. import basicauth
from datetime import date

router = APIRouter(tags=["sessions"])

# create session by owner id and conference id
@router.post("/sessions", response_model=schemas.Session)
def create_session_for_conference(
    session: schemas.SessionCreate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])
):
    conference=conferences_crud.get_conference_by_uuid(db, uuid=session.conference_id, owner_id=current_user.id)
    if conference is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=404, detail="Conference not found")
    if session.date < conference.start_date or session.date > conference.end_date or session.date < date.today():
        logging.exception("Invalid date")
        raise HTTPException(status_code=400, detail=f"Invalid date! Conference date is between {conference.start_date} and {conference.end_date} and today is {date.today()}")
    if session.start_time > session.end_time:
        logging.exception("Invalid time")
        raise HTTPException(status_code=400, detail="Invalid time")
    session=crud.create_conference_session(db=db, session=session, owner_id=current_user.id)
    logging.info("Session created: " + session.name)
    return session

# create sessions by list of sessions
@router.post("/sessions/list", response_model=list[schemas.Session])
def create_sessions_for_conference(
    sessions: list[schemas.SessionCreate], db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])
):
    if sessions is None or len(sessions) == 0:
        logging.exception("Invalid request body")
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    session_list=[]

    for session in sessions:
        conference=conferences_crud.get_conference_by_uuid(db, uuid=session.conference_id, owner_id=current_user.id)
        if conference is None:
            logging.exception("Conference not found")
            raise HTTPException(status_code=404, detail="Conference not found")
        if session.date < conference.start_date or session.date > conference.end_date or session.date < date.today():
            logging.exception("Invalid date")
            raise HTTPException(status_code=400, detail=f"Invalid date! Conference date is between {conference.start_date} and {conference.end_date} and today is {date.today()}")
        if session.start_time > session.end_time:
            logging.exception("Invalid time")
            raise HTTPException(status_code=400, detail="Invalid time")
        
    for session in sessions:
        session_list.append(crud.create_conference_session(db=db, session=session, owner_id=current_user.id))

    logging.info("Sessions created for conference: " + session.conference_id)
    return session_list

# get all sessions
@router.get("/sessions/all_sessions", response_model=list[schemas.Session])
def get_all_sessions(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if offset < 0 or limit < 0:
        logging.exception("Invalid query parameters")
        raise HTTPException(status_code=400, detail="Invalid query parameters")
    db_sessions = crud.get_sessions(db, offset=offset, limit=limit)
    if db_sessions is None or len(db_sessions) == 0:
        logging.exception("No sessions found")
        raise HTTPException(status_code=404, detail="Session not found")
    logging.info("Sessions retrieved")
    return db_sessions

# get all sessions by conference id
@router.get("/sessions/{conference_id}", response_model=list[schemas.Session])
def get_sessions_by_conference_id(conference_id: str, db: Session = Depends(get_db),basic_auth = Depends(basicauth.basic_auth)):
    if conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id) is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=404, detail="Conference not found")
    db_sessions = crud.get_all_sessions_by_uuid_id(db, conference_uuid=conference_id)
    if db_sessions is None or len(db_sessions) == 0:
        logging.exception("No sessions found")
        raise HTTPException(status_code=404, detail="Session not found")
    logging.info("Sessions retrieved for conference: " + conference_id)
    return db_sessions

# update session
@router.put("/sessions", response_model=schemas.Session)
def update_session(session: schemas.SessionUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    if session.name is None and session.date is None and session.start_time is None and session.end_time is None and session.description is None and session.speakers is None and session.tags is None and session.location is None:
        logging.exception("Invalid request body")
        raise HTTPException(status_code=400, detail="Invalid request body")
    if conferences_crud.get_conference_by_uuid(db, uuid=session.conference_id,owner_id=current_user.id) is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=404, detail="Conference not found")
    db_session = crud.get_session_by_uuid_id(db, uuid=session.id, owner_id=current_user.id)
    if db_session is None:
        logging.exception("Session not found")
        raise HTTPException(status_code=404, detail="Session not found")
    conference=conferences_crud.get_conference_by_uuid(db, uuid=session.conference_id, owner_id=current_user.id)
    if session.date is not None and (session.date < conference.start_date or session.date > conference.end_date or session.date < date.today()):
        logging.exception("Invalid date")
        raise HTTPException(status_code=400, detail="Invalid date")
    if session.start_time is not None and session.end_time is not None and session.start_time > session.end_time:
        logging.exception("Invalid time")
        raise HTTPException(status_code=400, detail="Invalid time")
    updated_session = crud.update_session(db=db, session=session, uuid=session.id, owner_id=current_user.id)
    logging.info("Session updated: " + db_session.name)
    return updated_session

#delete session
@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    db_session = crud.get_session_by_uuid_id(db, uuid=session_id, owner_id=current_user.id)
    if db_session is None:
        logging.exception("Session not found")
        raise HTTPException(status_code=404, detail="Session not found")
    session_deleted = crud.delete_session(db=db, uuid=session_id, owner_id=current_user.id)
    logging.info("Session deleted: " + db_session.name)
    return session_deleted