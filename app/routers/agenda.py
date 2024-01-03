from fastapi import APIRouter, HTTPException, Depends, Security, status
import logging
from app.schemas.user_schemas import UserAuthentication as User
from app.oauth2 import get_current_active_user
from ..dependencies import get_db
from sqlalchemy.orm import Session
from ..schemas import agenda_schemas as schemas
from ..crud import agenda_crud as crud, attendee_crud, conferences_crud, sessions_crud
from ..models import Session
from ..basicauth import basic_auth

router = APIRouter(tags=["agenda"])

# create agenda
@router.post("/agenda", response_model=schemas.Agenda, status_code=status.HTTP_201_CREATED)
def create_agenda(agenda: schemas.AgendaCreate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    if attendee_crud.get_attendee_by_id(db, attendee_id=current_user.id) is None:
        logging.exception("Attendee not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendee not found")
    if attendee_crud.get_attendee_conference_by_attendee_id_and_conference_id(db, attendee_id=current_user.id, conference_id=agenda.conference_id) is None:
        logging.exception("Attendee not registered for conference")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    db_agenda = crud.get_agenda(db, conference_id=agenda.conference_id, attendee_id=current_user.id)
    if db_agenda:
        logging.exception("Agenda already registered")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Agenda already registered")
    for session_id in agenda.sessions:
        if sessions_crud.get_session_by_conference_uuid_session_uuid(db, session_id=session_id, conference_id=agenda.conference_id) is None:
            logging.exception("Session not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    created_agenda = crud.create_agenda(db=db, conference_id=agenda.conference_id,attendee_id=current_user.id, agenda=agenda)
    if isinstance(created_agenda, Session):
        session = {
            "id" : created_agenda.uuid,
            "name" : created_agenda.name,
            "date" : created_agenda.date.isoformat(),
            "start_time" : created_agenda.start_time.isoformat(),
            "end_time" : created_agenda.end_time.isoformat(),
            "description" : created_agenda.description,
            "location" : created_agenda.location,
            "speakers" : created_agenda.speakers,
            "tags" : created_agenda.tags
        }
        logging.exception("Found conflict with a session")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"error":"found conflict with a session", "session": session})
    logging.info("Agenda created for: " + db_agenda.attendee_id)
    return created_agenda

# get all agenda
@router.get("/agenda", response_model=list[schemas.Agenda])
def get_all_agenda(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    agenda=crud.get_all_agenda(db, offset=offset, limit=limit)
    if agenda is None or len(agenda) == 0:
        logging.exception("No Agenda found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Agenda found")
    logging.info("All Agenda retrieved")
    return agenda

# get agenda by conference id and attendee id
@router.get("/agenda/{conference_id}", response_model=schemas.Agenda)
def get_agenda_by_conference_id_attendee_id(conference_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    if attendee_crud.get_attendee_by_id(db, attendee_id=current_user.id) is None:
        logging.exception("Attendee not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendee not found")
    if conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id) is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    agenda=crud.get_agenda_by_conference_uuid_attendee_uuid(db, conference_id=conference_id, attendee_id=current_user.id)
    if agenda is None:
        logging.exception("Agenda not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agenda not found")
    logging.info("Agenda retrieved for conference:" + conference_id)
    return agenda

@router.get("/agenda/attendee/{attendee_id}/conference/{conference_id}", response_model=schemas.Agenda)
def get_agenda_by_conference_id_attendee_id(conference_id: str, attendee_id: str, db: Session = Depends(get_db), basic_auth = Depends(basic_auth)):
    if attendee_crud.get_attendee_by_uuid(db, attendee_id=attendee_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendee not found")
    if conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    agenda=crud.get_agenda_for_attendee(db, conference_id=conference_id, attendee_id=attendee_id)
    if agenda is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agenda not found")
    return agenda

# update agenda by conference id and attendee id
@router.put("/agenda", response_model=schemas.Agenda)
def update_agenda(agenda: schemas.AgendaUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    if agenda.name is None and (agenda.sessions is None or len(agenda.sessions) == 0):
        logging.exception("Invalid request body")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")
    if attendee_crud.get_attendee_by_id(db, attendee_id=current_user.id) is None:
        logging.exception("Attendee not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendee not found")
    if conferences_crud.get_conference_by_conference_uuid(db, uuid=agenda.conference_id) is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    db_agenda = crud.get_agenda(db, conference_id=agenda.conference_id, attendee_id=current_user.id)
    if not db_agenda:
        logging.exception("Agenda not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agenda not found")
    if agenda.sessions is not None:
        for session_id in agenda.sessions:
            if sessions_crud.get_session_by_conference_uuid_session_uuid(db, session_id=session_id, conference_id=agenda.conference_id) is None:
                logging.exception("Session not found")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    updated_agenda = crud.update_agenda(db=db, conference_id=agenda.conference_id, attendee_id=current_user.id, agenda=agenda)
    if isinstance(updated_agenda,Session):
        session = {
            "id" : updated_agenda.uuid,
            "name" : updated_agenda.name,
            "date" : updated_agenda.date.isoformat(),
            "start_time" : updated_agenda.start_time.isoformat(),
            "end_time" : updated_agenda.end_time.isoformat(),
            "description" : updated_agenda.description,
            "location" : updated_agenda.location,
            "speakers" : updated_agenda.speakers,
            "tags" : updated_agenda.tags
        }
        logging.exception("Found conflict with a session")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"error":"found conflict with a session", "session": session})
    logging.info("Agenda updated for: " + db_agenda.attendee_id)
    return updated_agenda

# delete agenda by conference id and attendee id
@router.delete("/agenda/{conference_id}")
def delete_agenda(conference_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    if attendee_crud.get_attendee_by_id(db, attendee_id=current_user.id) is None:
        logging.exception("Attendee not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attendee not found")
    if conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id) is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    try:
        db_agenda = crud.get_agenda(db, conference_id=conference_id, attendee_id=current_user.id)
        if db_agenda is None:
            logging.exception("Agenda not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agenda not found")
    except:
        logging.exception("Agenda not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agenda not found")
    deleted_agenda = crud.delete_agenda(db=db, conference_id=conference_id, attendee_id=current_user.id)
    logging.info("Agenda deleted for conference: " + conference_id)
    return deleted_agenda
