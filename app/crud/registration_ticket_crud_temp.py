from datetime import datetime
from sqlalchemy.orm import Session
import uuid
import logging
from fastapi import HTTPException, status as Status

from app.models import RegistrationTicket
from app.schemas.registration_ticket_schema_temp import RegistrationTicketCreate

def get_registration_ticket_by_ticket_id(db: Session, ticket_id: str):
    return db.query(RegistrationTicket).filter(RegistrationTicket.ticket_id == ticket_id).first()

# get registration tickets by ticket_id but all the tickets having same registration_order_item_id
def get_registration_tickets_by_registration_order_item_id(db: Session, registration_order_item_id: int):
    return db.query(RegistrationTicket).filter(RegistrationTicket.registration_order_item_id == registration_order_item_id).all()
 
def create_registration_ticket(db: Session, registration_ticket: RegistrationTicketCreate, tid_str: str):
    tkt_uuid = "tkt-"+str(uuid.uuid4())
    registration_ticket_db = RegistrationTicket(
        registration_order_item_id=registration_ticket.registration_order_item_id,
        uuid= tkt_uuid,
        checked_in=registration_ticket.checked_in,
        created_on=datetime.now(),
        ticket_id = f'{tid_str}-{tkt_uuid[4:6]}'
    )
    db.add(registration_ticket_db)
    db.commit()
    db.refresh(registration_ticket_db)
    return registration_ticket_db

def update_registration_ticket(db: Session, ticket_id: str, registration_ticket: RegistrationTicketCreate):
    registration_ticket_db = get_registration_ticket_by_ticket_id(db, ticket_id)
    if registration_ticket_db is None:
        raise HTTPException(status_code=Status.HTTP_404_NOT_FOUND, detail="Registration ticket not found")
    registration_ticket_db.registration_order_item_id = registration_ticket.registration_order_item_id
    registration_ticket_db.checked_in = registration_ticket.checked_in
    db.commit()
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