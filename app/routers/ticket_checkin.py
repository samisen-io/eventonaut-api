from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import attendee_checkin_crud as crud, conferences_crud
from ..oauth2 import get_current_active_user
from ..schemas.user_schemas import UserAuthentication as User
from ..static_enums.role import RoleEnum
from ..schemas import ticket_checkin_schemas as schemas
import logging
from ..import models

router = APIRouter(tags=["attendee check-in"], prefix="/check-in")

@router.get("/", response_model=schemas.Ticket)
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
    conference_ticket = TicketMapper(conference_ticket)
    return conference_ticket

@router.post("/", response_model=schemas.CheckInResponse)
def check_in_attendee(request: schemas.TicketCheckIn, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, RoleEnum.REGISTRATION_STAFF.name])):
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
    if conference_ticket.checked_in:
        logging.exception(f"Ticket with id {request.ticket_id} already checked in")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ticket already checked in")
    updated_ticket = crud.member_check_in(db, conference_ticket)
    response = schemas.CheckInResponse(message="Ticket checked in successfully", ticket=TicketMapper(updated_ticket))
    logging.info(f"Ticket with id {request.ticket_id} checked in successfully")
    return response

def TicketMapper(Ticket: models.RegistrationTicket):
    ticket = schemas.Ticket(ticket_id=Ticket.ticket_id, event_id=Ticket.registration_order_item.registration_order.event_id, checked_in=Ticket.checked_in)
    return ticket