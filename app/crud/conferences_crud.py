from fastapi import HTTPException
import logging
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.pinecone_operations import delete_namespace

from .. import models
from ..schemas import conference_schemas as schemas, ai_assistant_schemas as assistant_schemas
from . import agenda_crud
from .. import AI_assitant
import uuid
from ..code_generator import generate_unique_string

# get all conferences ordered by start date in descending order
def get_all_conferences(db: Session, offset: int = 0, limit: int = 100):
    conferences = db.query(models.Conference).offset(offset).limit(limit).all()
    return conferences

def get_all_conferences_for_attendee(db: Session, offset: int = 0, limit: int = 100):
    conferences = db.query(models.Conference).filter(models.Conference.start_date >= datetime.utcnow().date()).order_by(models.Conference.start_date).offset(offset).limit(limit).all()
    return conferences

def get_conferences_by_owner_id(db: Session, owner_id: int):
    confernces = db.query(models.Conference).filter(models.Conference.owner_id == owner_id).all()
    return confernces

def get_conference_by_code(db: Session, code: str):
    conference = db.query(models.Conference).filter(models.Conference.code == code).first()
    return conference

# create conference
def create_user_conference(db: Session, conference: schemas.ConferenceCreate, user_id: int):
    client_id = conference.model_dump().pop("client_id")
    db_conference = models.Conference(**conference.model_dump(), owner_id=user_id)
    db_conference.client_id = db.query(models.Client).filter(models.Client.uuid == client_id).first().id if client_id is not None else None
    db_conference.created_on = datetime.utcnow()
    db_conference.updated_on = datetime.utcnow()
    db_conference.uuid = "evt-" + str(uuid.uuid4())
    assistant = assistant_schemas.AssistantCreate(model="gpt-3.5-turbo-1106", name=f"ca_{db_conference.uuid}", description="Conference Assistant", instructions="You are conference assitant. You can help users with their queries related to the sessions of the conference to build their agenda/schedule.", tools=[{"type": "code_interpreter"}])
    db_conference.assistant_id = AI_assitant.create_assistant(schema=assistant).id
    
    while True:
        try:
            db_conference.code = generate_unique_string()
            break
        except:
            print("Duplicate conference-code found! Attempting to generate new code...")
            continue

    db.add(db_conference)
    db.commit()
    db.refresh(db_conference)
    return db_conference

def get_conf_by_uuid(db:Session, conference_id: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id).first()
    return conference

# get conference by uuid and owner id
def get_conference_by_uuid(db: Session, uuid: str, owner_id: int):
    conference = db.query(models.Conference).filter(models.Conference.uuid == uuid, models.Conference.owner_id == owner_id).first()
    return conference

def get_conference_by_conference_uuid(db: Session, uuid: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == uuid).first()
    return conference

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
    if conference.assistant_id is not None and conference.assistant_id != "None":
        AI_assitant.delete_assistant(assistant_id=conference.assistant_id)
    db.query(models.Conference_Files).filter(models.Conference_Files.conference_id == conference.id).delete()
    delete_namespace(conference_id=conference.uuid)
    db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.conference_id == conference.id).delete()
    db.delete(conference)
    db.commit()
    
    return True

# update conference by conference id
def update_user_conference(db: Session, conference: schemas.ConferenceCreate, uuid: str, owner_id:int):
    db_conference = db.query(models.Conference).filter(models.Conference.uuid == uuid,models.Conference.owner_id == owner_id).first()

    updates = {
        'name': conference.name,
        'location': conference.location,
        'venue_name': conference.venue_name,
        'venue_location': conference.venue_location,
        'start_date': conference.start_date,
        'end_date': conference.end_date,
        'description': conference.description,
        'conference_logo': conference.conference_logo,
        'timezone': conference.timezone,
        'registration_link': conference.registration_link,
        'information_guide': conference.information_guide,
        'conference_banner_url': conference.conference_banner_url
    }

    for key, value in updates.items():
        if value is not None:
            setattr(db_conference, key, value)

    if db_conference.start_date > db_conference.end_date or db_conference.start_date < date.today():
        logging.exception("Invalid date range")
        raise HTTPException(status_code=400, detail="Invalid date range")

    db_conference.client_id = db.query(models.Client).filter(models.Client.uuid == conference.client_id).first().id if conference.client_id is not None else None

    db_conference.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_conference)
    return db_conference

def upload_file_id(db: Session, file_id: str, conference_id: str, owner_id: int):
    conference = db.query(models.Conference).filter(models.Conference.owner_id == owner_id, models.Conference.uuid == conference_id).first()
    db_file = models.Conference_Files(file_id = file_id, conference_id = conference.id)
    db_file.created_on = datetime.utcnow()
    db_file.updated_on = datetime.utcnow()
    db_file.uuid = "cnf-" + str(uuid.uuid4())
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    print(f"File_Id - {file_id} uploaded to DB")
    return True

def delete_file_id(db: Session, file_id: str, conference_id: str, owner_id: int):
    conference = db.query(models.Conference).filter(models.Conference.owner_id == owner_id, models.Conference.uuid == conference_id).first()
    db_file = db.query(models.Conference_Files).filter(models.Conference_Files.file_id == file_id, models.Conference_Files.conference_id == conference.id).first()
    db.delete(db_file)
    db.commit()
    print(f"File_Id - {file_id} Deleted from DB")
    return True

def get_file_ids_by_conference_id(db, conference_id):
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id).first()
    files = db.query(models.Conference_Files).filter(models.Conference_Files.conference_id == conference.id).all()
    file_ids = [file.file_id for file in files]
    return file_ids

def get_assistant_id_by_conference_id(db, conference_id):
    conference = db.query(models.Conference).filter(models.Conference.uuid == conference_id).first()
    return conference.assistant_id