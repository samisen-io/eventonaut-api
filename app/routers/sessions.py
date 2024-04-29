from fastapi import APIRouter, HTTPException, Depends, Security, status
import logging
from sqlalchemy.orm import Session
from app import models
from app.schemas.user_schemas import UserAuthentication as User
from app.oauth2 import get_current_active_organization, get_current_active_user
from app.static_enums.role import RoleEnum
from ..schemas import session_schemas as schemas
from ..crud import sessions_crud as crud, conferences_crud, speakers_crud
from ..dependencies import get_db
from datetime import date
from ..basicauth import basic_auth
from ..schemas.session_speaker_schema import SessionResponse

router = APIRouter(tags=["sessions"])

@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session_for_conference(session: schemas.SessionCreate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    conference=conferences_crud.get_conference_by_uuid(db, uuid=session.conference_id, owner_id=current_user.id)
    if conference is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    if session.date < conference.start_date or session.date > conference.end_date or session.date < date.today():
        logging.exception("Invalid date")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid date! Date must fall under Conference date range!!")
    if session.start_time > session.end_time:
        logging.exception("Invalid time")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid time")
    session_speaker_ids = []
    if session.speakers is not None and len(session.speakers) > 0:
        for speaker_id in session.speakers:
            speaker = speakers_crud.get_speaker_by_uuid(db, uuid=speaker_id, owner_id=current_user.id)
            print(speaker)
            if speaker is None:
                logging.exception("Speaker not found")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speaker not found")
            if speaker.id not in session_speaker_ids:
                session_speaker_ids.append(speaker.id)
    session=crud.create_conference_session(db=db, session=session, owner_id=current_user.id,conference_id=conference.id, speaker_ids=session_speaker_ids)
    logging.info("Session created: " + session.uuid)
    return session

@router.post("/sessions/list", response_model=list[SessionResponse])
def create_sessions_for_conference(sessions: list[schemas.SessionCreate], db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    if sessions is None or len(sessions) == 0:
        logging.exception("Invalid request body")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")
    
    session_list=[]

    for session in sessions:
        conference=conferences_crud.get_conference_by_uuid(db, uuid=session.conference_id, owner_id=current_user.id)
        if conference is None:
            logging.exception("Conference not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
        if session.date < conference.start_date or session.date > conference.end_date or session.date < date.today():
            logging.exception(f"Invalid date! Conference date is between {conference.start_date} and {conference.end_date} and today is {date.today()}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid date! Date should fall under conference date range")
        if session.start_time > session.end_time:
            logging.exception("Invalid time")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid time")
        session_speaker_ids = []
        if session.speakers is not None and len(session.speakers) > 0:
            for speaker_id in session.speakers:
                speaker = speakers_crud.get_speaker_by_uuid(db, uuid=speaker_id, owner_id=current_user.id)
                if speaker is None:
                    logging.exception("Speaker not found")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speaker not found")
                if speaker.id not in session_speaker_ids:
                    session_speaker_ids.append(speaker.id)
        session_list.append(crud.create_conference_session(db=db, session=session, owner_id=current_user.id,conference_id=conference.id, speaker_ids=session_speaker_ids))

    logging.info("Sessions created for conference: " + session.conference_id)
    return session_list

@router.get("/sessions/by_organization", response_model=list[SessionResponse])
def get_sessions_by_organization_id(offset: int = 0, limit: int = 100, db: Session = Depends(get_db), organization: models.Organization = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    db_sessions = crud.get_sessions_by_organization_id(db, organization_id=organization.id, offset=offset, limit=limit)
    if db_sessions is None or len(db_sessions) == 0:
        logging.exception("No sessions found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    logging.info(f"Sessions retrieved for organization: {organization.id} ")
    return db_sessions

@router.get("/sessions/all_sessions", response_model=list[SessionResponse])
def get_all_sessions(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if offset < 0 or limit < 0:
        logging.exception("Invalid query parameters")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid query parameters")
    db_sessions = crud.get_sessions(db, offset=offset, limit=limit)
    if db_sessions is None or len(db_sessions) == 0:
        logging.exception("No sessions found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    logging.info("Sessions retrieved")
    return db_sessions

@router.get("/sessions/{conference_id}", response_model=list[SessionResponse])
def get_sessions_by_conference_id(conference_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    if conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id) is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    db_sessions = crud.get_all_sessions_by_uuid_id(db, conference_uuid=conference_id)
    if db_sessions is None or len(db_sessions) == 0:
        logging.exception("No sessions found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    logging.info("Sessions retrieved for conference: " + conference_id)
    return db_sessions

@router.put("/sessions", response_model=SessionResponse)
def update_session(session: schemas.SessionUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    validate_session_update(session)
    conference = get_conference(session, db, current_user)
    db_session = get_db_session(session, db, current_user)
    validate_date_and_time(session, conference)
    session_speaker_ids = get_speaker_ids(session, db, current_user)
    updated_session = crud.update_session(db=db, session=session, db_session=db_session, speaker_ids=session_speaker_ids)
    logging.info("Session updated: " + updated_session.uuid)
    return updated_session

def validate_session_update(session):
    session_dict = session.model_dump()
    session_dict.pop('id')
    session_dict.pop('conference_id')
    if all(value is None for value in session_dict.values()):
        logging.exception("Invalid request body")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")

def get_conference(session, db, current_user):
    conference = conferences_crud.get_conference_by_uuid(db, uuid=session.conference_id,owner_id=current_user.id)
    if conference is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    return conference

def get_db_session(session, db, current_user):
    db_session = crud.get_session_by_uuid_id(db, uuid=session.id, owner_id=current_user.id)
    if db_session is None:
        logging.exception("Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return db_session

def validate_date_and_time(session, conference):
    if session.date is not None and (session.date < conference.start_date or session.date > conference.end_date or session.date < date.today()):
        logging.exception("Invalid date")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date")
    if session.start_time is not None and session.end_time is not None and session.start_time > session.end_time:
        logging.exception("Invalid time")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid time")

def get_speaker_ids(session, db, current_user):
    session_speaker_ids = []
    if session.speakers is not None and len(session.speakers) > 0:
        for speaker_id in session.speakers:
            speaker = speakers_crud.get_speaker_by_uuid(db, uuid=speaker_id, owner_id=current_user.id)
            if speaker is None:
                logging.exception("Speaker not found")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Speaker not found")
            if speaker.id not in session_speaker_ids:
                session_speaker_ids.append(speaker.id)
    return session_speaker_ids

@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    db_session = crud.get_session_by_uuid_id(db, uuid=session_id, owner_id=current_user.id)
    if db_session is None:
        logging.exception("Session not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    session_deleted = crud.delete_session(db=db, db_session=db_session)
    logging.info("Session deleted: " + db_session.name)
    return session_deleted