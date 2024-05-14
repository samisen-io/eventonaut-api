from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import attendee_exhibitors_crud, attendee_crud, exhibitor_crud
from ..oauth2 import get_current_active_user
from ..static_enums.role import RoleEnum
from ..static_enums.event_types import EventTypeEnum
from .. schemas import attendee_exhibitor_schemas as schemas
import logging
from .. import models

router = APIRouter(tags=["attendee_exhibitors"], prefix="/attendee_exhibitors")

def attendee_exhibitor_mapper(conference_id: int, exhibitors: list[models.Exhibitor]):
    exhibitor_responses = [schemas.ExhibitorResponse(**exhibitor.__dict__) for exhibitor in exhibitors] if exhibitors else []
    return schemas.AttendeeExhibitorResponse(conference_id=conference_id, exhibitors=exhibitor_responses)

@router.get("/", response_model=schemas.AttendeeExhibitorResponse)
def get_exhibitors_for_conference(conference_id: str, db: Session = Depends(get_db), current_user: dict = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name])):
    attendee = attendee_crud.get_attendee_by_id(db, current_user.id)
    attendee_conference = attendee_crud.get_attendee_conference_by_attendee_id_and_conference_id(db, attendee_id=current_user.id, conference_id=conference_id)
    if attendee_conference is None:
        logging.exception("Attendee not registered for Event")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if attendee_conference.conference.event_type.upper() != EventTypeEnum.TRADESHOW.name:
        logging.exception("Event is not a trade show")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event is not a trade show")
    exhibitors = attendee_exhibitors_crud.get_exhibitors_for_conference(db, attendee.id, attendee_conference.conference_id)
    if exhibitors is None or len(exhibitors) == 0:
        logging.exception("No Exhibitors found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Exhibitors found")
    attendee_exhibitors = attendee_exhibitor_mapper(conference_id, exhibitors)
    return attendee_exhibitors

@router.put("/", response_model=schemas.AttendeeExhibitorResponse)
def create_attendee_exhibitor(attendee_exhibitor: schemas.AttendeeExhibitorCreate, db: Session = Depends(get_db), current_user: dict = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name])):
    attendee = attendee_crud.get_attendee_by_id(db, current_user.id)
    attendee_conference = attendee_crud.get_attendee_conference_by_attendee_id_and_conference_id(db, attendee_id=current_user.id, conference_id=attendee_exhibitor.conference_id)
    if attendee_conference is None:
        logging.exception("Attendee not registered for Event")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if attendee_conference.conference.event_type.upper() != EventTypeEnum.TRADESHOW.name:
        logging.exception("Event is not a trade show")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event is not a trade show")
    exhibitor_ids = []
    if attendee_exhibitor.exhibitor_ids is not None and len(attendee_exhibitor.exhibitor_ids) > 0:
        for exhibitor_id in attendee_exhibitor.exhibitor_ids:
            exhibitor = exhibitor_crud.get_exhibitor(db, exhibitor_id, attendee_conference.conference_id)
            if exhibitor is None:
                logging.exception("Exhibitor not found")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibitor not found")
            if exhibitor.id not in exhibitor_ids:
                exhibitor_ids.append(exhibitor.id)
    attendee_exhibitors = attendee_exhibitors_crud.create_attendee_exhibitor(db, attendee.id, exhibitor_ids, attendee_conference.conference_id)
    attendee_exhibitors = attendee_exhibitor_mapper(attendee_exhibitor.conference_id, attendee_exhibitors)
    return attendee_exhibitors