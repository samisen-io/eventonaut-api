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
    available_tickets_dict = {item.uuid: item.available_quantity for item in available_tickets.registration_setup_items}

    if all(ticket.count == 0 for ticket in checkout_request.tickets):
        logging.exception("Select at least one ticket")
        raise HTTPException(status_code=400, detail="Select at least one ticket")

    extra_tickets = [{'ticket_id': ticket.id, 'extra_ticket_count': ticket.count - available_tickets_dict[ticket.id]} for ticket in checkout_request.tickets if ticket.id in available_tickets_dict and ticket.count > available_tickets_dict[ticket.id]]
    if extra_tickets:
        logging.exception(f"Extra tickets: {extra_tickets}")
        raise HTTPException(status_code=400, detail={"Extra tickets": extra_tickets})
    
def verify_ticket_types(checkout_request: CheckoutRequest, available_tickets: RegistrationSetupResponse):
    available_ticket_types = [item.uuid for item in available_tickets.registration_setup_items]
    checkout_ticket_types = [ticket.id for ticket in checkout_request.tickets]
    
    invalid_ticket_types = [ticket for ticket in checkout_ticket_types if ticket not in available_ticket_types]
    
    if invalid_ticket_types:
        logging.exception(f"Invalid ticket types: {invalid_ticket_types}")
        raise HTTPException(status_code=400, detail=f"Invalid ticket types: {invalid_ticket_types}")

def available_tickets_for_event(db: Session, event: models.Conference):
    setup = registration_setup_crud.get_setup_details(db, event.id)
    if setup is None:
        logging.exception(f"Registration setup for event {event.uuid} not found")
        raise HTTPException(status_code=404, detail=f"Registration setup for event {event.uuid} not found")
    if not setup.is_live:
        logging.exception(f"Tickets for event id {event.uuid} are not live")
        raise HTTPException(status_code=400, detail=f"Tickets for event id {event.uuid} are not live")
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
            if ticket["id"] in available_tickets:
                available_tickets[ticket["id"]] -= ticket["count"] if available_tickets[ticket["id"]] >= ticket["count"] else 0
    setup = update_setup_with_available_tickets(setup, available_tickets)
    return setup
                
def get_db_available_tickets(db: Session, setup: RegistrationSetupResponse):
    available_tickets = {}
    for item in setup.registration_setup_items:
        available_tickets[item.uuid] = item.available_quantity
    return available_tickets
    
def update_setup_with_available_tickets(setup: RegistrationSetupResponse, available_tickets: dict):
    for item in setup.registration_setup_items:
        if item.uuid in available_tickets:
            item.available_quantity = available_tickets[item.uuid]
    return setup