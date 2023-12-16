from fastapi import HTTPException
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
    for conference in conferences:
        conference.__dict__.pop('client_id')
    return conferences

def get_all_conferences_for_attendee(db: Session, offset: int = 0, limit: int = 100):
    conferences = db.query(models.Conference).filter(models.Conference.start_date >= datetime.utcnow().date()).order_by(models.Conference.start_date).offset(offset).limit(limit).all()
    for conference in conferences:
        conference.__dict__.pop('client_id')
    return conferences

def get_conferences_by_owner_id(db: Session, owner_id: int):
    return db.query(models.Conference).filter(models.Conference.owner_id == owner_id).all()

def get_conference_by_code(db: Session, code: str):
    return db.query(models.Conference).filter(models.Conference.code == code).first()

# create conference
def create_user_conference(db: Session, conference: schemas.ConferenceCreate, user_id: int):
    client_id = conference.model_dump().pop("client_id")
    db_conference = models.Conference(**conference.model_dump(), owner_id=user_id)
    if conference.description is None:
        db_conference.description = "None"
    if conference.conference_logo is None:
        db_conference.conference_logo = "None"
    if conference.description is None or conference.description.strip() == "" or conference.description == "string" or conference.description == "None":
        db_conference.description = "None"
    if conference.conference_logo is None or conference.conference_logo.strip() == "" or conference.conference_logo == "string" or conference.conference_logo == "None":
        db_conference.conference_logo = "None"
    if client_id is None:
        db_conference.client_id = "None"
    else:
        db_conference.client_id = db.query(models.Client).filter(models.Client.uuid == client_id).first().id
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
            print("Duplicate code found")
            continue
    db.add(db_conference)
    db.commit()
    db.refresh(db_conference)
    db_conference.__dict__.pop('client_id')
    return db_conference

def get_conf_by_uuid(db:Session, conference_id: str):
    return db.query(models.Conference).filter(models.Conference.uuid == conference_id).first()

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
        'start_date': conference.start_date,
        'end_date': conference.end_date,
        'description': conference.description if conference.description is not None else "None",
        'conference_logo': conference.conference_logo if conference.conference_logo is not None else "None",
        'timezone': conference.timezone,
        'registration_link': conference.registration_link if conference.registration_link is not None else "None",
        'information_guide': conference.information_guide if conference.information_guide is not None else 'None'
    }

    for key, value in updates.items():
        if value is not None:
            setattr(db_conference, key, value)

    if conference.start_date is not None and conference.end_date is not None:
        if conference.start_date > conference.end_date or conference.start_date < date.today():
            raise HTTPException(status_code=400, detail="Invalid date range")
        
    attributes = ["description", "conference_logo", "timezone", "registration_link", "client_id", "information_guide"]

    for attr in attributes:
        value = getattr(conference, attr)
        if value is None or value.strip() in ("", "string", "None"):
            setattr(db_conference, attr, "None")

    if conference.client_id is not None:
        db_conference.client_id = db.query(models.Client).filter(models.Client.uuid == conference.client_id).first().id
    else:
        db_conference.client_id = None

    db_conference.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_conference)
    db_conference.__dict__.pop('client_id')
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