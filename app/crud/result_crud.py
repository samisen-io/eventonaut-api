import datetime
from sqlalchemy.orm import Session
from app.crud import conferences_crud
from app.schemas import conference_schemas, venue_schemas
from app.static_enums.event import EventEnum
from app.static_enums.session import SessionEnum
from .. import models
from ..schemas import result_schemas

def get_objects(db: Session, objects: list[str]):
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
        'evt': result_schemas.Event,
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

    # final_objects = []
    # rank = 1
    # for obj in objects:
    #     code = obj[:3]
    #     if code not in models_table.keys():
    #         return False
    #     elif code == 'evt':
    #         db_obj = db.query(models_table[code]).filter(models_table[code].uuid == obj).first()
    #         if db_obj is None:
    #             return False
    #         venue = db.query(models.Venue).filter(models.Venue.id == db_obj.venue_id).first()
    #         db_obj.venue_details = venue.__dict__
    #         # db_obj.status = EventEnum(db_obj.conference_status_id).name
    #         db_obj = db_obj.__dict__
    #         db_obj['status'] = EventEnum(db_obj['conference_status_id']).name
    #         db_obj.rank = rank
    #         rank += 1
    #         final_objects.append(schemas_table[code](**db_obj.__dict__))
    #     elif code == 'ses':
    #         db_obj = db.query(models_table[code]).filter(models_table[code].uuid == obj).first()
    #         if db_obj is None:
    #             return False
    #         db_obj.status = SessionEnum(db_obj.session_status_id).name
    #         db_obj.rank = rank
    #         rank += 1
    #         final_objects.append(schemas_table[code](**db_obj.__dict__))
    #     else:
    #         db_obj = db.query(models_table[code]).filter(models_table[code].uuid == obj).first()
    #         if db_obj is None:
    #             return False
    #         db_obj = db_obj.__dict__
    #         db_obj['rank'] = rank
    #         rank += 1
    #         final_objects.append(schemas_table[code](**db_obj))

    # return final_objects
    
    final_objects = []
    rank = 1
    for obj in objects:
        code = obj[:3]
        if code not in models_table.keys():
            return False
        elif code == 'evt':
            db_obj = db.query(models_table[code]).filter(models_table[code].uuid == obj).first()
            if db_obj is None:
                return False
            venue = db.query(models.Venue).filter(models.Venue.id == db_obj.venue_id).first()
            db_obj.venue_details = venue.__dict__
            db_obj.rank = rank
            db_obj = db_obj.__dict__
            db_obj['status'] = EventEnum(db_obj['conference_status_id']).name 
            rank += 1
            final_objects.append(schemas_table[code](**db_obj))
        elif code == 'ses':
            db_obj = db.query(models_table[code]).filter(models_table[code].uuid == obj).first()
            if db_obj is None:
                return False
            db_obj.rank = rank
            db_obj = db_obj.__dict__
            db_obj['status'] = SessionEnum(db_obj['session_status_id']).name
            rank += 1
            final_objects.append(schemas_table[code](**db_obj))
        else:
            db_obj = db.query(models_table[code]).filter(models_table[code].uuid == obj).first()
            if db_obj is None:
                return False
            db_obj = db_obj.__dict__
            db_obj['rank'] = rank
            rank += 1
            final_objects.append(schemas_table[code](**db_obj))

    return final_objects