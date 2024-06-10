from sqlalchemy.orm import Session
from .. import models
from sqlalchemy.orm import contains_eager

def get_ticket(db: Session, ticket_id: str):
    return db.query(models.RegistrationTicket).filter(models.RegistrationTicket.ticket_id == ticket_id).first()

def get_conference_ticket(db: Session, ticket_id: str, conference: models.Conference):
    return db.query(models.RegistrationTicket).join(models.RegistrationOrderItem, models.RegistrationOrderItem.id == models.RegistrationTicket.registration_order_item_id).join(models.RegistrationSetupItem, models.RegistrationOrderItem.registration_setup_item_id == models.RegistrationSetupItem.id).options(contains_eager(models.RegistrationTicket.registration_order_item).contains_eager(models.RegistrationOrderItem.registration_order), contains_eager(models.RegistrationTicket.registration_order_item).contains_eager(models.RegistrationOrderItem.registration_setup_item)).filter(models.RegistrationTicket.ticket_id == ticket_id, models.RegistrationOrder.event_id == conference.id).first()

def member_check_in(db: Session, ticket: models.RegistrationTicket):
    ticket.checked_in = True
    db.commit()
    db.refresh(ticket)
    return ticket

def get_all_attendees_with_tickets(db: Session, conference_id: int):
    return db.query(models.Attendee).join(models.User, models.Attendee.user_id == models.User.id).join(models.RegistrationOrder, (models.Attendee.id == models.RegistrationOrder.attendee_id) & (models.RegistrationOrder.event_id == conference_id)).join(models.RegistrationOrderItem, models.RegistrationOrder.id == models.RegistrationOrderItem.registration_order_id).join(models.RegistrationSetupItem, models.RegistrationOrderItem.registration_setup_item_id == models.RegistrationSetupItem.id).join(models.RegistrationTicket, models.RegistrationOrderItem.id == models.RegistrationTicket.registration_order_item_id).options(contains_eager(models.Attendee.user),contains_eager(models.Attendee.registration_order).contains_eager(models.RegistrationOrder.registration_order_item).contains_eager(models.RegistrationOrderItem.registration_ticket),contains_eager(models.Attendee.registration_order).contains_eager(models.RegistrationOrder.registration_order_item).contains_eager(models.RegistrationOrderItem.registration_setup_item)).all()