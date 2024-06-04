from sqlalchemy.orm import Session
import uuid
import logging
from fastapi import HTTPException, status as Status

from app.models import RegistrationTicket
from app.schemas.registration_ticket_schema_temp import RegistrationTicketCreate

def get_registration_ticket_by_ticket_id(db: Session, ticket_id: str):
    return db.query(RegistrationTicket).filter(RegistrationTicket.ticket_id == ticket_id).first()

def create_registration_ticket(db: Session, registration_ticket: RegistrationTicketCreate):
    registration_ticket_db = RegistrationTicket(
        registration_order_item_id=registration_ticket.registration_order_item_id,
        ticket_id="tkt-"+str(uuid.uuid4()),  # generate a new UUID for ticket_id
        checked_in=registration_ticket.checked_in
    )
    db.add(registration_ticket_db)
    db.commit()
    db.refresh(registration_ticket_db)
    return registration_ticket_db

def delete_registration_ticket(db: Session, ticket_id: str):
    registration_ticket = get_registration_ticket_by_ticket_id(db, ticket_id)
    if registration_ticket is None:
        raise HTTPException(status_code=Status.HTTP_404_NOT_FOUND, detail="Registration ticket not found")
    db.delete(registration_ticket)
    db.commit()
    return registration_ticket

def check_in_registration_ticket(db: Session, ticket_id: str):
    registration_ticket = get_registration_ticket_by_ticket_id(db, ticket_id)
    if registration_ticket is None:
        raise HTTPException(status_code=Status.HTTP_404_NOT_FOUND, detail="Registration ticket not found")
    registration_ticket.checked_in = True
    db.commit()
    return registration_ticket

def get_registration_tickets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(RegistrationTicket).offset(skip).limit(limit).all()