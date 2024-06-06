from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.registration_setup_schemas import RegistrationSetupResponse
from app.schemas.checkout_schemas import CheckoutRequest
from app.crud import redis_crud, registration_setup_crud
from ..schemas.ticket_session_schemas import TicketSession
from ..import models
import logging
import json

def check_for_extra_tickets(checkout_request: CheckoutRequest, available_tickets: RegistrationSetupResponse):
    available_tickets_dict = {item.name: item.available_quantity for item in available_tickets.registration_setup_items}

    if all(ticket.count == 0 for ticket in checkout_request.tickets):
        raise HTTPException(status_code=400, detail="Select at least one ticket")

    extra_tickets = [{'ticket_name': ticket.name, 'extra_ticket_count': ticket.count - available_tickets_dict[ticket.name]} for ticket in checkout_request.tickets if ticket.name in available_tickets_dict and ticket.count > available_tickets_dict[ticket.name]]
    if extra_tickets:
        raise HTTPException(status_code=400, detail={"Extra tickets": extra_tickets})
    
def verify_ticket_types(checkout_request: CheckoutRequest, available_tickets: RegistrationSetupResponse):
    available_ticket_types = [item.name.casefold() for item in available_tickets.registration_setup_items]
    checkout_ticket_types = [ticket.name.casefold() for ticket in checkout_request.tickets]
    
    invalid_ticket_types = [ticket for ticket in checkout_ticket_types if ticket not in available_ticket_types]
    
    if invalid_ticket_types:
        raise HTTPException(status_code=400, detail=f"Invalid ticket types: {invalid_ticket_types}")

def available_tickets_for_event(db: Session, event: models.Conference):
    setup = registration_setup_crud.get_setup_details(db, event.id)
    if setup is None:
        logging.exception(f"Registration setup for event {event.uuid} not found")
        raise HTTPException(status_code=404, detail=f"Registration setup for event {event.uuid} not found")
    list_of_sessions = redis_crud.get_list_of_sessions_from_redis(event.uuid)
    if not list_of_sessions:
        redis_crud.delete_list_from_redis(event.uuid)
        return setup
    available_tickets = get_db_available_tickets(db, setup)
    for session_id in list_of_sessions:
        session_bytes = redis_crud.get_session_from_redis(session_id)
        if session_bytes is None:
            redis_crud.remove_session_from_list(event.uuid, session_id)
            continue
        session: TicketSession = json.loads(session_bytes)
        for ticket in session["tickets"]:
            if ticket["name"].casefold() in available_tickets:
                available_tickets[ticket["name"].casefold()] -= ticket["count"] if available_tickets[ticket["name"].casefold()] >= ticket["count"] else 0
    setup = update_setup_with_available_tickets(setup, available_tickets)
    return setup
                
def get_db_available_tickets(db: Session, setup: RegistrationSetupResponse):
    available_tickets = {}
    for item in setup.registration_setup_items:
        available_tickets[item.name.casefold()] = item.available_quantity
    return available_tickets
    
def update_setup_with_available_tickets(setup: RegistrationSetupResponse, available_tickets: dict):
    lower_case_tickets = {k.casefold(): v for k, v in available_tickets.items()}
    for item in setup.registration_setup_items:
        lower_case_name = item.name.casefold()
        if lower_case_name in lower_case_tickets:
            item.available_quantity = lower_case_tickets[lower_case_name]
    return setup