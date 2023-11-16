from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from .. import models
from ..schemas import conference_schemas as schemas, ai_assistant_schemas as assistant_schemas
from . import agenda_crud
from .. import AI_assitant
from pytz import timezone
import uuid
from ..uuid_generator import generate_unique_string

# get all conferences ordered by start date in descending order
def get_all_conferences(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.Conference).offset(offset).limit(limit).all()

def get_all_conferences_for_attendee(db: Session, offset: int = 0, limit: int = 100):
    return db.query(models.Conference).filter(models.Conference.start_date >= datetime.now(timezone('Asia/Kolkata')).date()).order_by(models.Conference.start_date).offset(offset).limit(limit).all()

def get_conferences_by_owner_id(db: Session, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.owner_id == owner_id).all()

def get_conference_by_code(db: Session, code: str):
    return db.query(models.Conference).filter(models.Conference.code.ilike(code)).first()

# create conference
def create_user_conference(db: Session, conference: schemas.ConferenceCreate, user_id: int):
    db_conference = models.Conference(**conference.model_dump(), owner_id=user_id)
    if conference.description is None:
        db_conference.description = "None"
    if conference.conference_logo is None:
        db_conference.conference_logo = "None"
    tz = timezone('Asia/Kolkata')
    if conference.description is None or conference.description.strip() == "" or conference.description == "string" or conference.description == "None":
        db_conference.description = "None"
    if conference.conference_logo is None or conference.conference_logo.strip() == "" or conference.conference_logo == "string" or conference.conference_logo == "None":
        db_conference.conference_logo = "None"
    db_conference.created_on = datetime.now(tz)
    db_conference.updated_on = datetime.now(tz)
    db_conference.uuid = str(uuid.uuid4())
    assistant = assistant_schemas.AssistantCreate(model="gpt-4-1106-preview", name=f"ca_{db_conference.uuid}", description="Conference Assistant", instructions="You are conference assitant. You can help users with their queries related to the sessions of the conference to build their agenda/schedule.")
    db_conference.assistant_id = AI_assitant.create_assistant(schema=assistant).id
    
    while True:
        try:
            db_conference.code = generate_unique_string()
            break
        except:
            print("Duplicate code found")
            continue

    db.add(db_conference)
    db.commit()
    db.refresh(db_conference)
    return db_conference

# get conference by uuid and owner id
def get_conference_by_uuid(db: Session, uuid: str, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.uuid == uuid, models.Conference.owner_id == owner_id).first()

def get_conference_by_conference_uuid(db: Session, uuid: str):
    return db.query(models.Conference).filter(models.Conference.uuid == uuid).first()

# delete conference by conference id
def delete_conference(db: Session, owner_id: int, uuid: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == uuid, models.Conference.owner_id == owner_id).first()
    if conference is None:
        return False
    sessions = db.query(models.Session).filter(models.Session.conference_id == conference.id, models.Session.owner_id == owner_id)
    if sessions is None:
        return False
    for session in sessions:
        db.delete(session)
    db.query(models.Settings).filter(models.Settings.conference_id == conference.id, models.Settings.owner_id == owner_id).delete()
    agenda_crud.delete_agenda_by_conference_id(db, conference_id=conference.id)
    AI_assitant.delete_assistant(assistant_id=conference.assistant_id)
    db.delete(conference)
    db.commit()
    return True

# update conference by conference id
def update_user_conference(db: Session, conference: schemas.ConferenceCreate, uuid: str, owner_id:int):
    db_conference = db.query(models.Conference).filter(models.Conference.uuid == uuid,models.Conference.owner_id == owner_id).first()
    tz = timezone('Asia/Kolkata')

    updates = {
        'name': conference.name,
        'location': conference.location,
        'start_date': conference.start_date,
        'end_date': conference.end_date,
        'description': conference.description if conference.description is not None else "None"
    }

    for key, value in updates.items():
        if value is not None:
            setattr(db_conference, key, value)

    if conference.start_date is not None and conference.end_date is not None:
        if conference.start_date > conference.end_date or conference.start_date < date.today():
            raise HTTPException(status_code=400, detail="Invalid date range")
        
    if conference.description is None or conference.description.strip() == "" or conference.description == "string" or conference.description == "None":
        db_conference.description = "None"
        
    if conference.conference_logo is None or conference.conference_logo.strip() == "" or conference.conference_logo == "string" or conference.conference_logo == "None":
        db_conference.conference_logo = "None"

    db_conference.updated_on = datetime.now(tz)
    db.commit()
    db.refresh(db_conference)
    return db_conference
