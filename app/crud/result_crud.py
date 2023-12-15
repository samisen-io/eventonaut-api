from sqlalchemy.orm import Session
from .. import models
from ..schemas import user_schemas as schemas
from datetime import datetime
from . import agenda_crud
import uuid

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
        'spk': models.Speaker
    }