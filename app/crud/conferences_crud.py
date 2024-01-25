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

def add_client_details_to_conference(db: Session, conference: dict):
    db_client = db.query(models.Client).filter(models.Client.id == conference.client_id).first()
    schema_client = None if db_client is None else schemas.ClientDetails(id=db_client.uuid, name=db_client.name)
    conference.client_details = schema_client
    return conference

def add_venue_details_to_conference(db: Session, conference: dict):
    db_venue = db.query(models.Venue).filter(models.Venue.id == conference.venue_id).first()
    conference.venue_name = db_venue.name
    conference.venue_location = db_venue.location
    return conference

# get all conferences ordered by start date in descending order
def get_all_conferences(db: Session, offset: int = 0, limit: int = 100):
    conferences = db.query(models.Conference).offset(offset).limit(limit).all()
    for conference in conferences:
        conference = add_client_details_to_conference(db=db, conference=conference)
        conference = add_venue_details_to_conference(db=db, conference=conference)
    return conferences

def get_all_conferences_for_attendee(db: Session, offset: int = 0, limit: int = 100):
    conferences = db.query(models.Conference).filter(models.Conference.start_date >= datetime.utcnow().date()).order_by(models.Conference.start_date).offset(offset).limit(limit).all()
    for conference in conferences:
        conference = add_client_details_to_conference(db=db, conference=conference)
        conference = add_venue_details_to_conference(db=db, conference=conference)
    return conferences

def get_conferences_by_owner_id(db: Session, owner_id: int):
    confernces = db.query(models.Conference).filter(models.Conference.owner_id == owner_id).all()
    for conference in confernces:
        conference = add_client_details_to_conference(db=db, conference=conference)
        conference = add_venue_details_to_conference(db=db, conference=conference)
    return confernces

def get_conference_by_code(db: Session, code: str):
    conference = db.query(models.Conference).filter(models.Conference.code == code).first()
    return conference

def create_user_conference(db: Session, conference: schemas.ConferenceCreate, user_id: int, venue_id: int):
    conference_dict = conference.model_dump()
    client_id = conference_dict.pop("client_id")
    conference_dict.pop('venue_id')
    db_conference = models.Conference(**conference_dict, owner_id=user_id, venue_id=venue_id)
    db_client = db.query(models.Client).filter(models.Client.uuid == client_id).first()
    db_conference.client_id = db_client.id if db_client is not None else None
    db_conference.created_on = db_conference.updated_on = datetime.utcnow()
    db_conference.uuid = "evt-" + str(uuid.uuid4())
    assistant = assistant_schemas.AssistantCreate(model="gpt-3.5-turbo-1106", name=f"ca_{db_conference.uuid}", description="Conference Assistant", instructions="You are conference assitant. You can help users with their queries related to the sessions of the conference to build their agenda/schedule.", tools=[{"type": "code_interpreter"}])
    db_conference.assistant_id = AI_assitant.create_assistant(schema=assistant).id

    while True:
        try:
            db_conference.code = generate_unique_string()
            break
        except:
            print("Duplicate conference-code found! Attempting to generate new code...")

    db.add(db_conference)
    db.commit()
    db.refresh(db_conference)
    db_conference = add_client_details_to_conference(db=db, conference=db_conference)
    db_conference = add_venue_details_to_conference(db=db, conference=db_conference)
    return db_conference

def get_conference_by_uuid(db: Session, uuid: str, owner_id: int):
    conference = db.query(models.Conference).filter(models.Conference.uuid == uuid, models.Conference.owner_id == owner_id).first()
    return conference

def get_conference_by_conference_uuid(db: Session, uuid: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == uuid).first()
    conference = add_client_details_to_conference(db=db, conference=conference) if conference is not None else None
    conference = add_venue_details_to_conference(db=db, conference=conference) if conference is not None else None
    return conference

def delete_conference(db: Session, conference: models.Conference):
    sessions = db.query(models.Session).filter(models.Session.conference_id == conference.id, models.Session.owner_id == conference.owner_id)
    if sessions is None:
        return False
    for session in sessions:
        db.delete(session)
    db.query(models.Settings).filter(models.Settings.conference_id == conference.id, models.Settings.owner_id == conference.owner_id).delete()
    agenda_crud.delete_agenda_by_conference_id(db, conference_id=conference.id)
    db.query(models.Conference_Files).filter(models.Conference_Files.conference_id == conference.id).delete()
    delete_namespace(conference_id=conference.uuid)
    db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.conference_id == conference.id).delete()
    db.delete(conference)
    db.commit()
    return True

def update_user_conference(db: Session, conference: schemas.ConferenceUpdate, db_conference: models.Conference):
    conference_dict = conference.model_dump()
    conference_dict.pop('id')
    conference_dict['venue_id'] = db.query(models.Venue).filter(models.Venue.uuid == conference_dict['venue_id']).first().id if conference_dict['venue_id'] is not None else None

    non_nullable_feilds = ['name','location','venue_id','start_date','end_date','information_guide']

    for key, value in conference_dict.items():
            if key in non_nullable_feilds:
                if value is not None:
                    setattr(db_conference,key,value)
            else:
                setattr(db_conference,key,value)

    if db_conference.start_date > db_conference.end_date or db_conference.start_date < date.today():
        logging.exception("Invalid date range")
        raise HTTPException(status_code=400, detail="Invalid date range")
    
    db_client = db.query(models.Client).filter(models.Client.uuid == conference.client_id).first()
    db_conference.client_id = db_client.id if db_client is not None else None
    db_conference.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_conference)
    # return db_conference
    db_conference = add_client_details_to_conference(db=db, conference=db_conference)
    db_conference = add_venue_details_to_conference(db=db, conference=db_conference)
    return db_conference

def get_event_list_summary(db: Session, owner_id: int):
    total_events = db.query(models.Conference).filter(models.Conference.owner_id == owner_id).count()
    first_event_start_date = db.query(models.Conference).filter(models.Conference.owner_id == owner_id).order_by(models.Conference.start_date).first().start_date
    last_event_end_date = db.query(models.Conference).filter(models.Conference.owner_id == owner_id).order_by(models.Conference.end_date.desc()).first().end_date
    total_clients = db.query(models.Client).filter(models.Client.owner_id == owner_id).count()

    db_conferences = db.query(models.Conference).filter(models.Conference.owner_id == owner_id).all()

    total_sponsors = 0
    total_attendees = 0

    for conference in db_conferences:
        total_sponsors += db.query(models.Sponsors).filter(models.Sponsors.conference_id == conference.id).count()
        total_attendees += db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.conference_id == conference.id).count()

    return schemas.ConferenceListSummary(no_of_events=total_events, first_event_start_date=first_event_start_date, last_event_end_date=last_event_end_date, no_of_sponsors=total_sponsors, no_of_clients=total_clients, number_of_attendees=total_attendees)