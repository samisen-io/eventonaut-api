from datetime import date, time
import json
from typing import List
from sqlalchemy.orm import Session, joinedload
from app import crud, models
from app.crud import conferences_crud, sessions_crud, speakers_crud
from app.schemas import conference_schemas, result_schemas, session_schemas, speaker_schemas, venue_schemas
from app.static_enums.event import EventEnum
from app.static_enums.session import SessionEnum

models_table = {
    # 'usr': models.User,
    'evt': models.Conference,
    'ses': models.Session,
    # 'set': models.Settings,
    # 'cnf': models.Conference_Files,
    'atd': models.Attendee,
    # 'ate': models.Attendee_Conferences,
    'aga': models.Agenda,
    'ags': models.AgendaSession,
    'ltk': models.LogoutToken,
    'cli': models.Client,
    'spk': models.Speakers
}

schemas_table = {
    # 'usr': result_schemas.User,
    'evt': result_schemas.Conference,
    'ses': result_schemas.Session,
    # 'set': result_schemas.Settings,
    # 'cnf': result_schemas.Conference_Files,
    'atd': result_schemas.Attendee,
    # 'ate': result_schemas.Attendee_Conferences,
    'aga': result_schemas.Agenda,
    'ags': result_schemas.AgendaSession,
    'ltk': result_schemas.LogoutToken,
    'cli': result_schemas.Client,
    'spk': result_schemas.Speakers
}

def get_conference(db:Session, uuid, rank):
    db_obj = conferences_crud.get_conference_by_conference_uuid(db, uuid=uuid)
    db_obj_dict = db_obj.__dict__.copy()
    db_obj_dict.pop('_sa_instance_state', None)
    venue = db.query(models.Venue).filter(models.Venue.id == db_obj.venue_id).first().__dict__
    venue.pop('_sa_instance_state', None)
    venue = venue_schemas.VenueResponse(**venue)
    db_obj_dict['venue'] = venue
    db_obj_dict['status'] = EventEnum(db_obj_dict['conference_status_id']).name
    db_obj_dict['rank'] = rank
    event_response = result_schemas.Conference(**db_obj_dict)
    return event_response

def get_session(db:Session, uuid, rank):
    db_obj = sessions_crud.get_session_by_session_uuid(db, uuid=uuid)
    db_obj_dict = db_obj.__dict__.copy()
    db_obj_dict.pop('_sa_instance_state', None)
    db_obj_dict['status'] = SessionEnum(db_obj_dict['session_status_id']).name
    db_obj_dict['speakers'] = [speaker_schemas.Speaker(**speaker.__dict__) for speaker in db_obj.speakers_list]
    db_obj_dict['rank'] = rank
    session_response = result_schemas.Session(**db_obj_dict)
    return session_response

def get_speaker(db:Session, uuid, rank):
    db_obj = speakers_crud.get_speaker(db, speaker_id=uuid)
    db_obj_dict = db_obj.__dict__.copy()
    db_obj_dict.pop('_sa_instance_state', None)
    db_obj_dict['rank'] = rank
    speaker_response = result_schemas.Speakers(**db_obj_dict)
    return speaker_response

def get_objects(db: Session, objects: list[str]):
    final_objects = []
    rank = 1
    for obj in objects:
        code = obj[:3]
        if code not in models_table.keys():
            return False
        elif code == 'evt':
            db_obj = get_conference(db, obj, rank)
        elif code == 'ses':
            db_obj = get_session(db, obj, rank)
        elif code == 'spk':
            db_obj = get_speaker(db, obj, rank)
        rank += 1
        final_objects.append(db_obj)
    json_ouput = convert_to_json(final_objects)
    return json_ouput

def convert_to_json(objects):
    objects_dict = [{k: datetime_to_str(v) for k, v in obj.__dict__.items() if not k.startswith('_')} for obj in objects]
    for item in objects_dict:
        if 'venue' in item and isinstance(item['venue'], venue_schemas.VenueResponse):
            item['venue'] = item['venue'].model_dump() # convert VenueResponse to dict
        if 'speakers' in item:
            item['speakers'] = [speaker.dict() for speaker in item['speakers']]  # convert SpeakerBase to dict
    json_data = json.dumps(objects_dict)
    return json_data

def datetime_to_str(dt):
    if isinstance(dt, date):
        return dt.strftime('%Y-%m-%d')
    elif isinstance(dt, time):
        return dt.strftime('%H:%M:%S')
    else:
        return dt