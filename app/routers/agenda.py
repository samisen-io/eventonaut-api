from fastapi import APIRouter, HTTPException, Depends
from ..dependencies import get_db
from sqlalchemy.orm import Session
from ..schemas import agenda_schemas as schemas
from ..crud import agenda_crud as crud, attendee_crud, conferences_crud, sessions_crud

router = APIRouter(tags=["agenda"])

# create agenda
@router.post("/agenda/attendee_id", response_model=schemas.Agenda)
def create_agenda(agenda: schemas.AgendaCreate, db: Session = Depends(get_db)):
    if attendee_crud.get_attendee_by_uuid(db, attendee_id=agenda.attendee_id) is None:
        raise HTTPException(status_code=400, detail="Attendee not found")
    if conferences_crud.get_conference_by_conference_uuid(db, uuid=agenda.conference_id) is None:
        raise HTTPException(status_code=400, detail="Conference not found")
    db_agenda = crud.get_agenda(db, conference_id=agenda.conference_id, attendee_id=agenda.attendee_id)
    if db_agenda:
        raise HTTPException(status_code=400, detail="Agenda already registered")
    for session_id in agenda.sessions:
        if sessions_crud.get_session_by_conference_uuid_session_uuid(db, session_id=session_id, conference_id=agenda.conference_id) is None:
            raise HTTPException(status_code=400, detail="Session not found")
    return crud.create_agenda(db=db, conference_id=agenda.conference_id,attendee_id=agenda.attendee_id, agenda=agenda)

# get all agenda
@router.get("/agenda", response_model=list[schemas.Agenda])
def get_all_agenda(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    agenda=crud.get_all_agenda(db, offset=offset, limit=limit)
    if agenda is None or len(agenda) == 0:
        raise HTTPException(status_code=404, detail="No Agenda found")
    return agenda

# get agenda by conference id and attendee id
@router.get("/agenda/attendee_id/{attendee_id}/conference_id/{conference_id}", response_model=schemas.Agenda)
def get_agenda_by_conference_id_attendee_id(conference_id: str, attendee_id: str, db: Session = Depends(get_db)):
    agenda=crud.get_agenda_by_conference_uuid_attendee_uuid(db, conference_id=conference_id, attendee_id=attendee_id)
    if agenda is None:
        raise HTTPException(status_code=404, detail="Agenda not found")
    return agenda

# update agenda by conference id and attendee id
@router.put("/agenda/attendee_id", response_model=schemas.Agenda)
def update_agenda(agenda: schemas.AgendaUpdate, db: Session = Depends(get_db)):
    if agenda.name is None and agenda.sessions is None:
        raise HTTPException(status_code=400, detail="Invalid request body")
    if attendee_crud.get_attendee_by_uuid(db, attendee_id=agenda.attendee_id) is None:
        raise HTTPException(status_code=400, detail="Attendee not found")
    if conferences_crud.get_conference_by_conference_uuid(db, uuid=agenda.conference_id) is None:
        raise HTTPException(status_code=400, detail="Conference not found")
    db_agenda = crud.get_agenda(db, conference_id=agenda.conference_id, attendee_id=agenda.attendee_id)
    if not db_agenda:
        raise HTTPException(status_code=400, detail="Agenda not found")
    if agenda.sessions is not None:
        for session_id in agenda.sessions:
            if sessions_crud.get_session_by_conference_uuid_session_uuid(db, session_id=session_id, conference_id=agenda.conference_id) is None:
                raise HTTPException(status_code=400, detail="Session not found")
    return crud.update_agenda(db=db, conference_id=agenda.conference_id, attendee_id=agenda.attendee_id, agenda=agenda)

# delete agenda by conference id and attendee id
@router.delete("/agenda/attendee_id/{attendee_id}/conference_id/{conference_id}")
def delete_agenda(conference_id: str, attendee_id: str, db: Session = Depends(get_db)):
    if attendee_crud.get_attendee_by_uuid(db, attendee_id=attendee_id) is None:
        raise HTTPException(status_code=400, detail="Attendee not found")
    if conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id) is None:
        raise HTTPException(status_code=400, detail="Conference not found")
    try:
        db_agenda = crud.get_agenda(db, conference_id=conference_id, attendee_id=attendee_id)
        if db_agenda is None:
            raise HTTPException(status_code=404, detail="Agenda not found")
    except:
        raise HTTPException(status_code=404, detail="Agenda not found")
    return crud.delete_agenda(db=db, conference_id=conference_id, attendee_id=attendee_id)
