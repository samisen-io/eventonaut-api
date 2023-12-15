from sqlalchemy.orm import Session
from .. import models

def get_objects(db: Session, objects: list[str]):
    tables = {
        'usr': models.User,
        'evt': models.Conference,
        'ses': models.Session,
        'set': models.Settings,
        'cnf': models.Conference_Files,
        'atd': models.Attendee,
        'ate': models.Attendee_Conferences,
        'aga': models.Agenda,
        'ags': models.AgendaSession,
        'ltk': models.LogoutToken,
        'cli': models.Client,
        'spk': models.Speakers
    }

    final_objects = []
    rank = 1

    for obj in objects:
        code = obj[:3]
        if code not in tables:
            return False
        else:
            db_obj = db.query(tables[code]).filter(tables[code].uuid == obj).first()
            if db_obj is None:
                return False
            db_obj = db_obj.model_dump()
            db_obj['rank'] = rank
            rank += 1
            final_objects.append(db_obj)

    return final_objects