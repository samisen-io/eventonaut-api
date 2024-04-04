from sqlalchemy.orm import Session
from .. import models
from ..schemas import agenda_schemas as schemas
from . import conferences_crud, sessions_crud
from datetime import datetime
import uuid
from sqlalchemy.orm import joinedload

def exclude_archived(agenda: models.Agenda):
    agenda.sessions = [session for session in agenda.sessions if not session.is_archived]

# create agenda
def create_agenda(db: Session, conference_id: str, attendee_id: int, agenda: schemas.AgendaCreate):
    session_ids = []
    for session_id in agenda.sessions:
        if session_id not in session_ids:
            session_ids.append(session_id)

    sessions = []
    for session_id in session_ids:
        session = sessions_crud.get_session_by_session_uuid(db, uuid=session_id)
        conflicting_session = None
    
        for s in sessions:
            if s.date == session.date:
                if (s.start_time >= session.start_time and s.start_time < session.end_time) or (s.end_time > session.start_time and s.end_time <= session.end_time) or (s.start_time <= session.start_time and s.end_time >= session.end_time):
                    conflicting_session = s
                    break

        if conflicting_session:
            return conflicting_session
        else:
            sessions.append(session)

    conference = conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id)
    attendee = db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    db_agenda = models.Agenda(conference_id=conference.id, name=agenda.name, attendee_id=attendee.id)
    db_agenda.created_on = datetime.utcnow()
    db_agenda.updated_on = datetime.utcnow()
    db_agenda.uuid = "aga-" + str(uuid.uuid4())
    db.add(db_agenda)
    db.commit()
    db.refresh(db_agenda)

    for session in sessions:
        db_agenda_session = models.AgendaSession(agenda_id=db_agenda.id, session_id=session.id, attendee_id=attendee.id, date=session.date, start_time=session.start_time, end_time=session.end_time)
        db_agenda_session.created_on = datetime.utcnow()
        db_agenda_session.updated_on = datetime.utcnow()
        db_agenda_session.uuid = "ags-" + str(uuid.uuid4())
        db.add(db_agenda_session)
        db.commit()
        db.refresh(db_agenda_session)
        
    agenda_session = db.query(models.Agenda).options(joinedload(models.Agenda.sessions).joinedload(models.Session.agenda)).filter(models.Agenda.id == db_agenda.id).first()
    exclude_archived(agenda_session)
    return agenda_session

# return all the agendas with the list of sessions
def get_all_agenda(db: Session, offset: int = 0, limit: int = 100):
    agenda_sessions = db.query(models.Agenda).options(joinedload(models.Agenda.sessions).joinedload(models.Session.agenda)).offset(offset).limit(limit).all()
    for session in agenda_sessions:
        exclude_archived(session)
    return agenda_sessions

def get_agenda(db: Session, conference_id: str, attendee_id: int):
    conference=conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id)
    if conference is None:
        return None
    attendee=db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    db_agenda = db.query(models.Agenda).filter(models.Agenda.conference_id == conference.id,models.Agenda.attendee_id==attendee.id).first()
    if db_agenda is not None:
        exclude_archived(db_agenda)
    return db_agenda

# get agenda by conference id and attendee id
def get_agenda_by_conference_uuid_attendee_uuid(db: Session, conference_id: str, attendee_id: int):
    conference=conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id)
    if conference is None:
        return None
    attendee=db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    db_agenda = db.query(models.Agenda).filter(models.Agenda.conference_id == conference.id,models.Agenda.attendee_id==attendee.id).first()
    if db_agenda is None:
        return None
    agenda_session = db.query(models.Agenda).options(joinedload(models.Agenda.sessions).joinedload(models.Session.agenda)).filter(models.Agenda.id == db_agenda.id).first()
    exclude_archived(agenda_session)
    return agenda_session

def get_agenda_for_attendee(db: Session, conference_id: int, attendee_id: int):
    db_agenda = db.query(models.Agenda).filter(models.Agenda.conference_id == conference_id, models.Agenda.attendee_id==attendee_id).first()
    if db_agenda is None:
        return None
    agenda_session = db.query(models.Agenda).options(joinedload(models.Agenda.sessions).joinedload(models.Session.agenda)).filter(models.Agenda.id == db_agenda.id).first()
    exclude_archived(agenda_session)
    return agenda_session

# update agenda by conference id and attendee id
def update_agenda(db: Session, conference_id: str, attendee_id: int, agenda: schemas.AgendaUpdate):

    if agenda.sessions is not None:
        session_ids = []
        for session_id in agenda.sessions:
            if session_id not in session_ids:
                session_ids.append(session_id)

        sessions = []
        for session_id in session_ids:
            session = sessions_crud.get_session_by_session_uuid(db, uuid=session_id)
            conflicting_session = None

            for s in sessions:
                if s.date == session.date:
                    if (s.start_time >= session.start_time and s.start_time < session.end_time) or (s.end_time > session.start_time and s.end_time <= session.end_time) or (s.start_time <= session.start_time and s.end_time >= session.end_time):
                        conflicting_session = s
                        break

            if conflicting_session:
                return conflicting_session
            else:
                sessions.append(session)

    conference=conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id)
    attendee=db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    db_agenda = db.query(models.Agenda).filter(models.Agenda.conference_id == conference.id,models.Agenda.attendee_id==attendee.id).first()
    db_agenda.updated_on=datetime.utcnow()

    if agenda.name is not None:
        db_agenda.name = agenda.name

    if agenda.sessions is not None:
        db.query(models.AgendaSession).filter(models.AgendaSession.agenda_id == db_agenda.id).delete()

        for session in sessions:
            db_agenda_session = models.AgendaSession(agenda_id=db_agenda.id, session_id=session.id, attendee_id=attendee.id, date=session.date, start_time=session.start_time, end_time=session.end_time)
            db_agenda_session.created_on = datetime.utcnow()
            db_agenda_session.updated_on = datetime.utcnow()
            db_agenda_session.uuid = "ags-" + str(uuid.uuid4())
            db.add(db_agenda_session)
            db.commit()
            db.refresh(db_agenda_session)
    db.commit()
    db.refresh(db_agenda)
    
    agenda_session = db.query(models.Agenda).options(joinedload(models.Agenda.sessions).joinedload(models.Session.agenda)).filter(models.Agenda.id == db_agenda.id).first()
    exclude_archived(agenda_session)
    return agenda_session

# delete agenda by conference id and attendee id
def delete_agenda(db: Session, conference_id: str, attendee_id: int):
    conference=conferences_crud.get_conference_by_conference_uuid(db, uuid=conference_id)
    attendee=db.query(models.Attendee).filter(models.Attendee.user_id == attendee_id).first()
    db_agenda = db.query(models.Agenda).filter(models.Agenda.conference_id == conference.id,models.Agenda.attendee_id==attendee.id).first()
    db.query(models.AgendaSession).filter(models.AgendaSession.agenda_id == db_agenda.id).delete()
    db.delete(db_agenda)
    db.commit()
    return True

# delete agenda by conference id
def delete_agenda_by_conference_id(db: Session, conference_id: int):
    db_agenda = db.query(models.Agenda).filter(models.Agenda.conference_id == conference_id).first()
    if db_agenda is not None:
        db.query(models.AgendaSession).filter(models.AgendaSession.agenda_id == db_agenda.id).delete()
        db.delete(db_agenda)
        db.commit()
        return True
    else:
        return False