import os
from urllib.parse import urlparse
from fastapi import HTTPException
import logging
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.pinecone_operations import delete_namespace
from app.routers import upload_image
from .. import models
from ..schemas import conference_schemas as schemas, ai_assistant_schemas as assistant_schemas
from . import agenda_crud
from .. import AI_assitant
import uuid
from ..code_generator import generate_unique_string
from .client_crud import get_client
from ..static_enums import event

def add_sponsor_details_to_conference(db: Session, conference: dict):
    event_sponsors = db.query(models.EventSponsors).filter(models.EventSponsors.conference_id == conference.id).all()
    conference.sponsor_details = []
    for event_sponsor in event_sponsors:
        sponsor = db.query(models.Sponsors).filter(models.Sponsors.id == event_sponsor.sponsor_id).first()
        conference.sponsor_details.append(sponsor)
    return conference

def add_client_details_to_conference(db: Session, conference: dict):
    conference.client_details = get_client(db=db, client_id=conference.client_id) if conference.client_id is not None else None
    return conference

def add_venue_details_to_conference(db: Session, conference: dict):
    db_venue = db.query(models.Venue).filter(models.Venue.id == conference.venue_id).first()
    conference.venue_details = None if db_venue is None else db_venue
    return conference

# get all conferences ordered by start date in descending order
def get_all_conferences(db: Session, offset: int = 0, limit: int = 100):
    conferences = db.query(models.Conference).offset(offset).limit(limit).all()
    for conference in conferences:
        conference = add_client_details_to_conference(db=db, conference=conference)
        conference = add_venue_details_to_conference(db=db, conference=conference)
        conference = add_sponsor_details_to_conference(db=db, conference=conference)
        conference.status = event.EventEnum(conference.conference_status_id).name
    return conferences

def get_all_conferences_for_attendee(db: Session, offset: int = 0, limit: int = 100):
    conferences = db.query(models.Conference).filter(models.Conference.start_date >= datetime.utcnow().date(), models.Conference.isarchived == False).order_by(models.Conference.start_date).offset(offset).limit(limit).all()
    for conference in conferences:
        conference = add_client_details_to_conference(db=db, conference=conference)
        conference = add_venue_details_to_conference(db=db, conference=conference)
        conference = add_sponsor_details_to_conference(db=db, conference=conference)
        conference.status = event.EventEnum(conference.conference_status_id).name
    return conferences

def get_conferences_by_owner_id(db: Session, owner_id: int):
    confernces = db.query(models.Conference).filter(models.Conference.owner_id == owner_id, models.Conference.isarchived == False).all()
    for conference in confernces:
        conference = add_client_details_to_conference(db=db, conference=conference)
        conference = add_venue_details_to_conference(db=db, conference=conference)
        conference = add_sponsor_details_to_conference(db=db, conference=conference)
        conference.status = event.EventEnum(conference.conference_status_id).name
    return confernces

def get_conference_by_code(db: Session, code: str):
    conference = db.query(models.Conference).filter(models.Conference.code == code, models.Conference.isarchived == False).first()
    return conference

def create_user_conference(db: Session, conference: schemas.ConferenceCreate, user_id: int, venue_id: int, sponsor_ids: list[int]):
    conference_dict = conference.model_dump()
    client_id = conference_dict.pop("client_id")
    conference_dict.pop('venue_id')
    conference_dict.pop('sponsor_ids')
    conference_logo = conference_dict.pop("conference_logo")
    conference_banner_url = conference_dict.pop("conference_banner_url")
    conference_status = conference_dict.pop("status")
    db_conference = models.Conference(**conference_dict, owner_id=user_id, venue_id=venue_id)
    db_conference.conference_status_id = event.EventEnum[conference_status.upper()].value
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

    conference_logo_image = None
    conference_banner_image = None
    
    db_conference.conference_logo = upload_image.get_actual_url(image_url=conference_logo, new_blob_container="event-logos", new_blob_name=f"event-logo-{db_conference.uuid}") if conference_logo is not None else None

    db_conference.conference_banner_url = upload_image.get_actual_url(image_url=conference_banner_url, new_blob_container="event-banners", new_blob_name=f"event-banner-{db_conference.uuid}") if conference_banner_url is not None else None

    db.add(db_conference)
    try:
        db.commit()
    except Exception as e:
        upload_image.delete_blob_by_url(db_conference.conference_logo)
        upload_image.delete_blob_by_url(db_conference.conference_banner_url)
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    db.refresh(db_conference)

    if len(sponsor_ids) > 0 and sponsor_ids is not None:
        for sponsor_id in sponsor_ids:
            db_event_sponsor = models.EventSponsors(conference_id=db_conference.id, sponsor_id=sponsor_id)
            db_event_sponsor.created_on = db_event_sponsor.updated_on = datetime.utcnow()
            db_event_sponsor.uuid = "esp-" + str(uuid.uuid4())
            db.add(db_event_sponsor)
            db.commit()
            db.refresh(db_event_sponsor)
    
    db_conference = add_client_details_to_conference(db=db, conference=db_conference)
    db_conference = add_venue_details_to_conference(db=db, conference=db_conference)
    db_conference = add_sponsor_details_to_conference(db=db, conference=db_conference)
    db_conference.status = event.EventEnum(db_conference.conference_status_id).name
    return db_conference

def get_conference_by_uuid(db: Session, uuid: str, owner_id: int):
    conference = db.query(models.Conference).filter(models.Conference.uuid == uuid, models.Conference.owner_id == owner_id, models.Conference.isarchived == False).first()
    return conference

def get_conference_by_conference_uuid(db: Session, uuid: str):
    conference = db.query(models.Conference).filter(models.Conference.uuid == uuid, models.Conference.isarchived == False).first()
    if conference is None:
        return None
    conference = add_client_details_to_conference(db=db, conference=conference) if conference is not None else None
    conference = add_venue_details_to_conference(db=db, conference=conference) if conference is not None else None
    conference = add_sponsor_details_to_conference(db=db, conference=conference) if conference is not None else None
    conference.status = event.EventEnum(conference.conference_status_id).name if conference is not None else None
    return conference

def delete_conference(db: Session, conference: models.Conference):
    sessions = db.query(models.Session).filter(models.Session.conference_id == conference.id, models.Session.owner_id == conference.owner_id)
    if sessions is not None:
        for session in sessions:
            session.isarchived = True
    delete_namespace(conference_id=conference.uuid)
    conference.isarchived = True
    db.commit()
    return True

def update_user_conference(db: Session, conference: schemas.ConferenceUpdate, db_conference: models.Conference, sponsor_ids: list[int]):
    conference_dict = conference.model_dump()
    conference_dict.pop('id')
    conference_dict.pop('sponsor_ids')
    conference_status = conference_dict.pop("status")
    conference_logo = conference_dict.pop("conference_logo")
    conference_banner_url = conference_dict.pop("conference_banner_url")
    conference_dict['venue_id'] = db.query(models.Venue).filter(models.Venue.uuid == conference_dict['venue_id']).first().id if conference_dict['venue_id'] is not None else None

    non_nullable_feilds = ['name','location','venue_id','start_date','end_date','information_guide']

    if conference_status is not None:
        db_conference.conference_status_id = event.EventEnum[conference_status.upper()].value

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
    
    if conference_logo is not None:
        db_conference.conference_logo = upload_image.get_actual_url(image_url=conference_logo, new_blob_container="event-logos", new_blob_name=f"event-logo-{db_conference.uuid}")
    elif conference_logo is None and db_conference.conference_logo is not None:
        upload_image.delete_blob_by_url(db_conference.conference_logo)
        db_conference.conference_logo = None
        
    if conference_banner_url is not None:
        db_conference.conference_banner_url = upload_image.get_actual_url(image_url=conference_banner_url, new_blob_container="event-banners", new_blob_name=f"event-banner-{db_conference.uuid}")
    elif conference_banner_url is None and db_conference.conference_banner_url is not None:
        upload_image.delete_blob_by_url(db_conference.conference_banner_url)
        db_conference.conference_banner_url = None 
    
    db_conference.updated_on = datetime.utcnow()
    try:
        db.commit()
    except Exception as e:
        if conference_logo is not None:
            upload_image.delete_blob_by_url(db_conference.conference_logo)
        if conference_banner_url is not None:
            upload_image.delete_blob_by_url(db_conference.conference_banner_url)
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    db.refresh(db_conference)

    db.query(models.EventSponsors).filter(models.EventSponsors.conference_id == db_conference.id).delete()
    if len(sponsor_ids) > 0 and sponsor_ids is not None:
        for sponsor_id in sponsor_ids:
            db_event_sponsor = models.EventSponsors(conference_id=db_conference.id, sponsor_id=sponsor_id)
            db_event_sponsor.created_on = db_event_sponsor.updated_on = datetime.utcnow()
            db_event_sponsor.uuid = "esp-" + str(uuid.uuid4())
            db.add(db_event_sponsor)
            db.commit()
            db.refresh(db_event_sponsor)

    db_conference = add_client_details_to_conference(db=db, conference=db_conference)
    db_conference = add_venue_details_to_conference(db=db, conference=db_conference)
    db_conference = add_sponsor_details_to_conference(db=db, conference=db_conference)
    db_conference.status = event.EventEnum(db_conference.conference_status_id).name
    return db_conference

def get_event_list_summary(db: Session, owner_id: int):
    db_conferences = db.query(models.Conference).filter(models.Conference.owner_id == owner_id, models.Conference.isarchived == False).order_by(models.Conference.start_date).all()
    total_events = db_conferences.count()
    first_event_start_date = db_conferences[0].start_date
    last_event_end_date = db.query(models.Conference).filter(models.Conference.owner_id == owner_id, models.Conference.isarchived == False).order_by(models.Conference.end_date.desc()).first().end_date
    total_clients = db.query(models.Client).filter(models.Client.owner_id == owner_id, models.Client.isarchived == False).count()

    total_sponsors = 0
    total_attendees = 0

    for conference in db_conferences:
        db_event_sponsors_ids = db.query(models.EventSponsors.sponsor_id).filter(models.EventSponsors.conference_id == conference.id).all()
        db_event_sponsors_ids = set([sponsor_id[0] for sponsor_id in db_event_sponsors_ids])
        total_sponsors += len(db_event_sponsors_ids)
        total_attendees += db.query(models.Attendee_Conferences).filter(models.Attendee_Conferences.conference_id == conference.id).count()

    return schemas.ConferenceListSummary(no_of_events=total_events, first_event_start_date=first_event_start_date, last_event_end_date=last_event_end_date, no_of_sponsors=total_sponsors, no_of_clients=total_clients, number_of_attendees=total_attendees)