from fastapi import APIRouter, HTTPException, Depends
from ..dependencies import get_db
from sqlalchemy.orm import Session
from ..schemas import agenda_schemas as schemas
from ..crud import agenda_crud as crud, attendee_crud as attendee_crud, conferences_crud as conferences_crud

router = APIRouter(tags=["agenda"])

# create agenda
@router.post("/agenda/attendee_id/{attendee_id}/conference_id/{conference_id}", response_model=schemas.Agenda)
def create_agenda(conference_id: int,attendee_id: int, agenda: schemas.AgendaCreate, db: Session = Depends(get_db)):
    if conference_id <= 0 or attendee_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference_id or attendee_id")
    if attendee_crud.get_attendee_by_id(db, attendee_id=attendee_id) is None:
        raise HTTPException(status_code=400, detail="Attendee not found")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=400, detail="Conference not found")
    db_agenda = crud.get_agenda_by_conference_id_attendee_id(db, conference_id=conference_id, attendee_id=attendee_id)
    if db_agenda:
        raise HTTPException(status_code=400, detail="Agenda already registered")
    return crud.create_agenda(db=db, conference_id=conference_id,attendee_id=attendee_id, agenda=agenda)

# get all agenda
@router.get("/agenda", response_model=list[schemas.Agenda])
def get_all_agenda(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    agenda=crud.get_all_agenda(db, skip=skip, limit=limit)
    if agenda is None or len(agenda) == 0:
        raise HTTPException(status_code=404, detail="No Agenda found")
    return agenda

# get agenda by conference id and attendee id
@router.get("/agenda/attendee_id/{attendee_id}/conference_id/{conference_id}", response_model=schemas.Agenda)
def get_agenda_by_conference_id_attendee_id(conference_id: int, attendee_id: int, db: Session = Depends(get_db)):
    if conference_id <= 0 or attendee_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference_id or attendee_id")
    agenda=crud.get_agenda_by_conference_id_attendee_id(db, conference_id=conference_id, attendee_id=attendee_id)
    if agenda is None:
        raise HTTPException(status_code=404, detail="Agenda not found")
    return agenda

# get agenda by attendee id and name
@router.get("/agenda/attendee_id/{attendee_id}/name/{name}", response_model=list[schemas.Agenda])
def get_all_agendas_by_attendee_id_name(attendee_id: int, name: str, db: Session = Depends(get_db)):
    if attendee_id <= 0 or name.isnumeric():
        raise HTTPException(status_code=400, detail="Invalid attendee_id or name")
    agenda=crud.get_agendas_by_attendee_id_name(db, attendee_id=attendee_id, name=name)
    if agenda is None or len(agenda) == 0:
        raise HTTPException(status_code=404, detail="Agenda not found")
    return agenda

# update agenda by conference id and attendee id
@router.put("/agenda/attendee_id/{attendee_id}/conference_id/{conference_id}", response_model=schemas.Agenda)
def update_agenda(conference_id: int, attendee_id: int, agenda: schemas.AgendaCreate, db: Session = Depends(get_db)):
    if conference_id <= 0 or attendee_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference_id or attendee_id")
    if attendee_crud.get_attendee_by_id(db, attendee_id=attendee_id) is None:
        raise HTTPException(status_code=400, detail="Attendee not found")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=400, detail="Conference not found")
    db_agenda = crud.get_agenda_by_conference_id_attendee_id(db, conference_id=conference_id, attendee_id=attendee_id)
    if db_agenda is None:
        raise HTTPException(status_code=404, detail="Agenda not found")
    return crud.update_agenda(db=db, conference_id=conference_id, attendee_id=attendee_id, agenda=agenda)

# delete agenda by conference id and attendee id
@router.delete("/agenda/attendee_id/{attendee_id}/conference_id/{conference_id}")
def delete_agenda(conference_id: int, attendee_id: int, db: Session = Depends(get_db)):
    if conference_id <= 0 or attendee_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference_id or attendee_id")
    if attendee_crud.get_attendee_by_id(db, attendee_id=attendee_id) is None:
        raise HTTPException(status_code=400, detail="Attendee not found")
    if conferences_crud.get_conference(db, conference_id=conference_id) is None:
        raise HTTPException(status_code=400, detail="Conference not found")
    db_agenda = crud.get_agenda_by_conference_id_attendee_id(db, conference_id=conference_id, attendee_id=attendee_id)
    if db_agenda is None:
        raise HTTPException(status_code=404, detail="Agenda not found")
    return crud.delete_agenda(db=db, conference_id=conference_id, attendee_id=attendee_id)