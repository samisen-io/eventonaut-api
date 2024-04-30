from sqlalchemy.orm import Session, joinedload
from .. import models
import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import aliased

def get_exhibitors_for_conference(db: Session, attendee_id: int, conference_id: int):
    AE = models.AttendeeExhibitors
    return db.query(models.Exhibitor).join(AE).filter(AE.attendee_id == attendee_id, AE.conference_id == conference_id).all()

def create_attendee_exhibitor(db: Session, attendee_id: int, exhibitor_ids: list[int], conference_id: int):
    AE = models.AttendeeExhibitors
    existing_records = db.query(AE).filter(AE.attendee_id == attendee_id, AE.conference_id == conference_id).all()

    if not exhibitor_ids:
        for record in existing_records:
            db.delete(record)
        db.commit()
        return None

    for record in existing_records:
        if record.exhibitor_id in exhibitor_ids:
            record.updated_on = datetime.utcnow()
            exhibitor_ids.remove(record.exhibitor_id)
        else:
            db.delete(record)

    for exhibitor_id in exhibitor_ids:
        new_record = AE(attendee_id=attendee_id, exhibitor_id=exhibitor_id, conference_id=conference_id)
        new_record.created_on = new_record.updated_on = datetime.utcnow()
        new_record.uuid = 'aex-' + str(uuid.uuid4())
        db.add(new_record)

    db.commit()

    return get_exhibitors_for_conference(db, attendee_id, conference_id)