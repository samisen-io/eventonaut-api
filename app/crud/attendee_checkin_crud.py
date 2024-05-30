from sqlalchemy.orm import Session, joinedload
from .. import models

def get_ticket(db: Session, ticket_id: str):
    return db.query(models.RegistrationTicket).filter(models.RegistrationTicket.ticket_id == ticket_id).first()

def get_conference_ticket(db: Session, ticket_id: str, conference: models.Conference):
    return db.query(models.RegistrationTicket).options(joinedload(models.RegistrationTicket.registration_order_item).options(joinedload(models.RegistrationOrderItem.registration_order))).filter(models.RegistrationTicket.ticket_id == ticket_id, models.RegistrationOrder.event_id == conference.id).first()

def member_check_in(db: Session, ticket: models.RegistrationTicket):
    ticket.checked_in = True
    db.commit()
    db.refresh(ticket)
    return ticket