from collections import defaultdict
from datetime import timedelta
import uuid
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy import func
from sqlalchemy.orm import Session
from app import models
from app.crud.attendee_crud import get_attendees_by_user_id
from app.crud.conferences_crud import get_conference_by_conference_uuid, get_conference_by_id, get_conference_by_uuid
from app.crud.master_template_crud import get_master_template_by_id
from app.crud.registration_order_crud_temp import create_registration_order, create_registration_order_temp, get_registration_order_by_id, update_registration_order
from app.crud.registration_order_item_crud import create_registration_order_item, get_registration_order_items_by_event_id, get_registration_order_items_by_registration_setup_item_id
from app.crud.registration_setup_crud_temp import create_registration_setup, get_registration_setup, get_registration_setup_by_event_id
from app.crud.registration_setup_item_crud_temp import create_registration_setup_item, get_registration_setup_item, get_registration_setup_items_by_event_id, update_registration_setup_item
from app.crud.registration_ticket_crud_temp import create_registration_ticket, update_registration_ticket
from app.dependencies import get_db
from app.oauth2 import get_current_active_user
from app.report_generation_operations import generate_pdf_tickets
from app.schemas.registratin_setup_item_schema_temp import RegistrationSetupItemCreateTemp
from app.schemas.registration_order_item_schema_temp import RegistrationOrderItem, RegistrationOrderItemCreate, RegistrationOrderItemInput
from app.schemas.registration_order_schema_temp import RegistrationOrderCreate, RegistrationOrderCreateTemp
from app.schemas.registration_setup_schema_temp import RegistrationSetupCreateTemp
from app.schemas.registration_ticket_schema_temp import RegistrationTicketCreate
from app.schemas.user_schemas import User
from app.static_enums.role import RoleEnum


router = APIRouter(tags=["data_visualization"])

@router.post("/create_registration_setup/")
def create_setup(registration_setup: RegistrationSetupCreateTemp, current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"]), db: Session = Depends(get_db)):
    registration_setup_db = create_registration_setup(db, registration_setup)
    return registration_setup_db

@router.post("/create_registration_setup_item/")
def create_setup_item(registration_setup_item: RegistrationSetupItemCreateTemp, current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"]), db: Session = Depends(get_db)):
    # return registration_setup_item
    registration_setup_item_db = create_registration_setup_item(db, registration_setup_item)
    return registration_setup_item_db

@router.post("/create_registration_order/")
def create_order(event_id: int, current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,]), db: Session = Depends(get_db)):
    attendee = get_attendees_by_user_id(db, current_user.id)
    order = RegistrationOrderCreateTemp(event_id=event_id, attendee_id=attendee.id)
    registration_order = create_registration_order_temp(db, order)
    return registration_order

@router.post("/create_registration_order_item", response_model=RegistrationOrderItem)
def create_order_item(order_item: RegistrationOrderItemInput, current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,]), db: Session = Depends(get_db)):
    attendee = get_attendees_by_user_id(db, current_user.id)
    if attendee is None:
        raise HTTPException(status_code=400, detail="Attendee not found")
    order = get_registration_order_by_id(db, order_item.registration_order_id)
    registration_setup_item = get_registration_setup_item(db, order_item.registration_setup_item_id)
    setup = get_registration_setup(db, registration_setup_item.registration_setup_id)
    event = get_conference_by_id(db, setup.event_id)
    if order_item.quantity > registration_setup_item.available_quantity:
        raise HTTPException(status_code=400, detail="Quantity is greater than available quantity")
    unit_price = registration_setup_item.price
    tax_amount = unit_price * setup.tax_rate
    fee_amount = unit_price * setup.fee_amount
    total_amount = (unit_price + tax_amount + fee_amount) * order_item.quantity
    order_item = RegistrationOrderItemCreate(
        registration_order_id=order_item.registration_order_id,
        description=order_item.description,
        quantity=order_item.quantity,
        unit_price=unit_price,
        total_amount=total_amount,
        registration_setup_item_id=order_item.registration_setup_item_id,
        code=order_item.code
    )
    order_item = create_registration_order_item(db, order_item)
    registration_setup_item_dict = registration_setup_item.to_dict()
    registration_setup_item_dict["available_quantity"] -= order_item.quantity
    registration_setup_item = models.RegistrationSetupItem(**registration_setup_item_dict)
    registration_setup_item = update_registration_setup_item(db, registration_setup_item)
    order_dict = order.to_dict()
    order_dict["amount"] += unit_price*order_item.quantity
    order_dict["tax_amount"] += tax_amount*order_item.quantity
    order_dict["fee_amount"] += fee_amount*order_item.quantity
    order_dict["total_amount"] += total_amount
    order = models.RegistrationOrder(**order_dict)
    order = update_registration_order(db, order)
    
    template_id = 'tem-cbd6cb4a-fff3-4778-94a4-59b737561cdf'
    template = get_master_template_by_id(db, template_id)
    tickets = []
    for _ in range(order_item.quantity):
        tid_str = f'tk-{event.uuid[4:9]}-{order.uuid[4:7]}'
        new_ticket = create_registration_ticket(db, RegistrationTicketCreate(registration_order_item_id=order_item.id), tid_str)
        db.commit()
        tickets.append(new_ticket)
    pdf_ticket = generate_pdf_tickets(db, tickets[0],template, event, order, order_item, upload=True)
    for ticket in tickets:
        ticket.ticket_url = pdf_ticket['url']
        update_registration_ticket(db, ticket.ticket_id, ticket)
    return order_item
    
@router.get("/Event_revenue/")
def event_revenue(event_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    event = get_conference_by_conference_uuid(db, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    setup_items = get_registration_setup_items_by_event_id(db, event.id)
    revenue_by_setup_item = []
    for setup_item in setup_items:
        order_items = get_registration_order_items_by_registration_setup_item_id(db, setup_item.id)
        total_revenue = sum([order_item.quantity * order_item.unit_price for order_item in order_items])
        revenue_by_setup_item.append({"Item": setup_item.name, "amount": total_revenue})
    return revenue_by_setup_item

@router.get("/Ticket_sales/")
def ticket_sales(event_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    event = get_conference_by_conference_uuid(db, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    order_items = get_registration_order_items_by_event_id(db, event.id)
    date_totals = defaultdict(int)
    for order_item in order_items:
        date_totals[order_item.created_on.date()] += order_item.quantity
    daily_sales = [{'date': str(date), 'total_number': total} for date, total in date_totals.items()]
    daily_sales.sort(key=lambda x: x['date'])
    earliest_order_date = min(date_totals.keys())
    latest_order_date = max(date_totals.keys())
    day = earliest_order_date
    while day <= latest_order_date:
        if not any(d['date'] == str(day) for d in daily_sales):
            daily_sales.append({'date': str(day), 'total_number': 0})
        day += timedelta(days=1)
    daily_sales.sort(key=lambda x: x['date'])
    return daily_sales

