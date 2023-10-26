from sqlalchemy.orm import Session
from pytz import timezone
from .. import models
from ..schemas import agenda_schemas as schemas
from datetime import datetime
from pytz import timezone

# create agenda
def create_agenda(db: Session,conference_id: int, attendee_id: int, agenda: schemas.AgendaCreate):
    db_agenda = models.Agenda(conference_id=conference_id, name=agenda.name, attendee_id=attendee_id)
    tz = timezone('Asia/Kolkata')
    db_agenda.created_on=datetime.now(tz)
    db_agenda.updated_on=datetime.now(tz)
    db.add(db_agenda)
    db.commit()
    db.refresh(db_agenda)
    return db_agenda

# get all agenda
def get_all_agenda(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Agenda).offset(skip).limit(limit).all()

# get agenda by conference id and attendee id
def get_agenda_by_conference_id_attendee_id(db: Session, conference_id: int, attendee_id: int):
    return db.query(models.Agenda).filter(models.Agenda.conference_id == conference_id,models.Agenda.attendee_id==attendee_id).first()

# get agenda by attendee id and like name string
def get_agendas_by_attendee_id_name(db: Session, attendee_id: int, name: str):
    return db.query(models.Agenda).filter(models.Agenda.attendee_id == attendee_id,models.Agenda.name.ilike('%'+name+'%')).all()

# update agenda by conference id and attendee id
def update_agenda(db: Session, conference_id: int, attendee_id: int, agenda: schemas.AgendaCreate):
    db_agenda = db.query(models.Agenda).filter(models.Agenda.conference_id == conference_id,models.Agenda.attendee_id==attendee_id).first()
    db_agenda.name = agenda.name
    tz = timezone('Asia/Kolkata')
    db_agenda.updated_on=datetime.now(tz)
    db.commit()
    db.refresh(db_agenda)
    return db_agenda

# delete agenda by conference id and attendee id
def delete_agenda(db: Session, conference_id: int, attendee_id: int):
    db_agenda = db.query(models.Agenda).filter(models.Agenda.conference_id == conference_id,models.Agenda.attendee_id==attendee_id).first()
    db.delete(db_agenda)
    db.commit()
    return True