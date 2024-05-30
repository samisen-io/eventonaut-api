from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import attendee_checkin_crud as crud, conferences_crud
from ..oauth2 import get_current_active_user
from ..schemas.user_schemas import UserAuthentication as User
from ..static_enums.role import RoleEnum
from ..schemas import attendee_checkin_schemas as schemas
import logging

router = APIRouter(tags=["attendee check-in"], prefix="/check-in")

@router.get("/")
def get_check_in_attendee(ticket_id: str, event_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, RoleEnum.REGISTRATION_STAFF.name])):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        logging.exception(f"Ticket with id {ticket_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    conference = conferences_crud.get_conference(db, event_id)
    if not conference:
        logging.exception(f"Conference with id {event_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    conference_ticket = crud.get_conference_ticket(db, ticket_id, conference)
    if not conference_ticket:
        logging.exception(f"Ticket with id {ticket_id} not found in conference with id {event_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found in conference")
    return conference_ticket

@router.post("/")
def check_in_attendee(request: schemas.AttendeeCheckin, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, RoleEnum.REGISTRATION_STAFF.name])):
    ticket = crud.get_ticket(db, request.ticket_id)
    if not ticket:
        logging.exception(f"Ticket with id {request.ticket_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    conference = conferences_crud.get_conference(db, request.event_id)
    if not conference:
        logging.exception(f"Conference with id {request.event_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    conference_ticket = crud.get_conference_ticket(db, request.ticket_id, conference)
    if not conference_ticket:
        logging.exception(f"Ticket with id {request.ticket_id} not found in conference with id {request.event_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found in conference")
    updated_ticket = crud.member_check_in(db, conference_ticket)
    logging.info(f"Member with ticket id {request.ticket_id} checked in")
    return updated_ticket