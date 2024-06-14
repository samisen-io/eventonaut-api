from .. import models, schemas
from sqlalchemy.orm import Session, joinedload, contains_eager
import uuid
from datetime import datetime
from fastapi import HTTPException, status
from ..static_enums.order_items import OrderItems
from ..static_enums.payment_status import PaymentStatus
from ..routers.ticket_checkin import TicketMapper 

def registration_order_mapper(registration_setup: models.RegistrationSetup, session: dict, attendee_id: int):
    registration_order = models.RegistrationOrder()
    registration_order.uuid = f"ord-{uuid.uuid4()}"
    registration_order.created_on = registration_order.updated_on = datetime.utcnow()
    registration_order.event_id = registration_setup.event_id
    registration_order.attendee_id = attendee_id
    registration_order.amount = get_total_amount_from_session(registration_setup.registration_setup_items, session)
    registration_order.tax_amount = registration_order.amount * registration_setup.tax_rate
    registration_order.fee_amount = registration_order.amount * registration_setup.fee_amount
    registration_order.total_amount = registration_order.amount + registration_order.tax_amount + registration_order.fee_amount
    registration_order.payment_status = PaymentStatus.UNPAID.value
    return registration_order

def registration_order_item_mapper(registration_setup_items: list[models.RegistrationSetupItem], session: dict):
    registration_order_items = []
    for ticket in session["tickets"]:
        ticket_item = next((item for item in registration_setup_items if item.uuid == ticket["id"]), None)
        if ticket_item is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid ticket type {ticket['id']}")
        registration_order_item = models.RegistrationOrderItem()
        registration_order_item.uuid = f"roi-{uuid.uuid4()}"
        registration_order_item.created_on = registration_order_item.updated_on = datetime.utcnow()
        registration_order_item.registration_setup_item_id = ticket_item.id
        registration_order_item.description = ticket_item.description
        registration_order_item.quantity = ticket["count"]
        registration_order_item.unit_price = ticket_item.price
        registration_order_item.total_amount = ticket_item.price * ticket["count"]
        registration_order_item.code = OrderItems.TICKET.name
        registration_order_items.append(registration_order_item)
    return registration_order_items
    
def create_db_order(db: Session, registration_order: models.RegistrationOrder, registration_order_items: list[models.RegistrationOrderItem], razorpay_order_id: str):
    try:
        registration_order.external_order_id = razorpay_order_id
        db.add(registration_order)
        db.flush()
        for registration_order_item in registration_order_items:
            registration_order_item.registration_order_id = registration_order.id
            db.add(registration_order_item)
        db.commit()
        db.refresh(registration_order)
        return registration_order
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def get_registration_order(db: Session, event_id: int, order_id: str, attendee_id: int):
    return db.query(models.RegistrationOrder).options(joinedload(models.RegistrationOrder.registration_order_item)).filter(models.RegistrationOrder.external_order_id == order_id, models.RegistrationOrder.attendee_id == attendee_id, models.RegistrationOrder.event_id == event_id).first()

def deduct_tickets_from_available_quantity(db: Session, registration_setup: models.RegistrationSetup, session: dict):
    registration_setup_items = registration_setup.registration_setup_items
    for ticket in session["tickets"]:
        ticket_item = next((item for item in registration_setup_items if item.uuid == ticket["id"]), None)
        if ticket_item is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid ticket type {ticket['id']}")
        ticket_item.available_quantity -= ticket["count"]
        db.add(ticket_item)
    return registration_setup
        
def add_tickets(db: Session, registration_order: models.RegistrationOrder, event_id: str):
    tickets = []
    for registration_order_item in registration_order.registration_order_item:
        for _ in range(registration_order_item.quantity):
            ticket = models.RegistrationTicket()
            ticket.uuid = f"tkt-{uuid.uuid4()}"
            ticket.created_on = datetime.utcnow()
            ticket.ticket_id = f"tk-{event_id[4:9]}-{registration_order_item.uuid[4:7]}-{ticket.uuid[4:6]}"
            ticket.registration_order_item_id = registration_order_item.id
            db.add(ticket)
    db.commit()
    db_tickets = db.query(models.RegistrationTicket).join(models.RegistrationOrderItem, models.RegistrationOrderItem.id == models.RegistrationTicket.registration_order_item_id).join(models.RegistrationSetupItem, models.RegistrationOrderItem.registration_setup_item_id == models.RegistrationSetupItem.id).options(contains_eager(models.RegistrationTicket.registration_order_item).contains_eager(models.RegistrationOrderItem.registration_order), contains_eager(models.RegistrationTicket.registration_order_item).contains_eager(models.RegistrationOrderItem.registration_setup_item)).filter(models.RegistrationTicket.registration_order_item_id.in_([item.id for item in registration_order.registration_order_item])).all()
    for ticket in db_tickets:
        tickets.append(TicketMapper(ticket, event_id))
    return tickets

def get_total_amount_from_session(registration_setup_items: list[models.RegistrationSetupItem], session: dict):
    total_amount = 0
    for ticket in session["tickets"]:
        ticket_item = next((item for item in registration_setup_items if item.uuid == ticket["id"]), None)
        if ticket_item is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid ticket type {ticket['id']}")
        total_amount += ticket_item.price * ticket["count"]
    return total_amount