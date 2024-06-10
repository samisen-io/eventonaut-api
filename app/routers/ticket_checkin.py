from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from ..dependencies import get_db
from ..crud import conferences_crud, ticket_checkin_crud as crud
from ..oauth2 import get_current_active_user
from ..schemas.user_schemas import UserAuthentication as User
from ..static_enums.role import RoleEnum
from ..schemas import ticket_checkin_schemas as schemas
import logging
from ..static_enums.organizer import OrganizerEnum

router = APIRouter(tags=["ticket_checkin"], prefix="/ticket-checkin")

@router.get("/", response_model=schemas.Ticket)
def get_check_in_attendee(ticket_id: str, event_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, RoleEnum.REGISTRATION_STAFF.name])):
    organization_id = current_user.organization_user[0].organization_id
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        logging.exception(f"Ticket with id {ticket_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    conference = conferences_crud.get_conference_by_uuid(db, event_id, organization_id)
    if not conference:
        logging.exception(f"Conference with id {event_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    conference_ticket = crud.get_conference_ticket(db, ticket_id, conference)
    if not conference_ticket:
        logging.exception(f"Ticket with id {ticket_id} not found in conference with id {event_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found in conference")
    conference_ticket = TicketMapper(conference_ticket, event_id)
    return conference_ticket

@router.post("/", response_model=schemas.CheckInResponse)
def check_in_attendee(request: schemas.TicketCheckIn, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, RoleEnum.REGISTRATION_STAFF.name])):
    organization_id = current_user.organization_user[0].organization_id
    ticket = crud.get_ticket(db, request.ticket_id)
    if not ticket:
        logging.exception(f"Ticket with id {request.ticket_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    conference = conferences_crud.get_conference_by_uuid(db, request.event_id, organization_id)
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
    response = schemas.CheckInResponse(message="Ticket checked in successfully", ticket=TicketMapper(updated_ticket, request.event_id))
    logging.info(f"Ticket with id {request.ticket_id} checked in successfully")
    return response

@router.get("/attendees", response_model=list[schemas.AttendeeTickets])
def get_all_attendees_with_tickets(event_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, RoleEnum.REGISTRATION_STAFF.name])):
    organization_id = current_user.organization_user[0].organization_id
    conference = conferences_crud.get_conference_by_uuid(db, event_id, organization_id)
    if not conference:
        logging.exception(f"Conference with id {event_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    attendees = crud.get_all_attendees_with_tickets(db, conference.id)
    attendees = [AttendeeMapper(attendee, event_id) for attendee in attendees]
    return attendees

def AttendeeMapper(attendee, event_id: str):
    tickets = [TicketMapper(ticket_item, event_id) 
               for order in attendee.registration_order
               for item in order.registration_order_item
               for ticket_item in item.registration_ticket]
    attendee = schemas.AttendeeTickets(uuid = attendee.uuid,
                               email = attendee.user.email,
                               first_name = attendee.user.first_name,
                               last_name = attendee.user.last_name,
                               title = attendee.title,
                               company = attendee.user.company,
                               bio = attendee.bio,
                               share_my_profile = attendee.share_my_profile,
                               share_my_agenda = attendee.share_my_agenda,
                               profile_image_url = attendee.user.profile_image_url,
                               status = OrganizerEnum(attendee.user.user_status_id).name,
                               is_active = attendee.user.is_active,
                               tickets = tickets)
    return attendee

def TicketMapper(ticket_item, event_id: str):
    ticket = schemas.Ticket(
                    ticket_id=ticket_item.ticket_id, 
                    type=ticket_item.registration_order_item.registration_setup_item.name, 
                    event_id=event_id, 
                    checked_in=ticket_item.checked_in)
    return ticket