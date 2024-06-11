from operator import and_
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Security
from fastapi.responses import StreamingResponse
import requests

from app.basicauth import basic_auth
from app.crud.attendee_crud import get_an_attendee_by_id, get_attendees_by_user_id
from app.crud.conferences_crud import get_conference_by_conference_uuid, get_conference_by_id
from app.crud.master_template_crud import get_master_template_by_id
from app.crud.registration_order_crud_temp import create_registration_order, get_registration_order_by_id, get_registration_order_by_order_id
from app.crud.registration_order_item_crud import create_registration_order_item, delete_registration_order_item, get_registration_order_item_by_id, get_registration_order_item_by_uuid, get_registration_order_items_by_registration_order_id
from app.crud.registration_order_item_type_crud_temp import get_registration_order_item_type_by_code, get_registration_order_item_type_by_id
from app.crud.registration_ticket_crud_temp import create_registration_ticket, get_registration_ticket_by_ticket_id, update_registration_ticket
from app.crud.users_crud import get_user
from app.schemas import registration_ticket_schema_temp as reg_ticket_schemas
from app.schemas import ticket_schema_temp as ticket_schemas
from app.crud.template_crud import get_template_by_id
from app.oauth2 import get_current_active_user
from app.report_generation_operations import generate_input_data, generate_pdf_invoice, generate_pdf_ticket, generate_pdf_tickets, generate_report_using_template
from app.schemas.conference_schemas import ConferenceResponse
from app.schemas.registration_order_item_schema_temp import RegistrationOrderItem, RegistrationOrderItemCreate, RegistrationOrderItemResponse
from app.models import RegistrationOrder as RegistrationOrderModel
from app.models import RegistrationOrderItem as RegistrationOrderItemModel
from app.schemas.registration_order_schema_temp import RegistrationOrder, RegistrationOrderCreate
from app.schemas.report_schemas import Report
from app.schemas.user_schemas import User
from app.static_enums.role import RoleEnum
from app.utils import conference_to_dict
from ..dependencies import get_db
from app.models import Session
from sqlalchemy.orm import joinedload


router = APIRouter(tags = ['reports'])

@router.post('/create_ticket')
def create_ticket(ticket_input: ticket_schemas.CreateTicket, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,])):
    current_user_id = current_user.id
    attendee = get_attendees_by_user_id(db, current_user_id)
    event = get_conference_by_conference_uuid(db, ticket_input.event_id)
    registration_order_db = RegistrationOrderCreate(
        event_id=event.id,
        attendee_id=attendee.id,
        amount=ticket_input.amount,
        tax_amount=ticket_input.tax_amount,
        fee_amount=ticket_input.fee_amount,
    )
    registration_order_db = create_registration_order(db,registration_order_db)
    registration_order_item_type_code = get_registration_order_item_type_by_code(db, ticket_input.code).code
    registration_order_item_db = RegistrationOrderItemCreate(
        registration_order_id= registration_order_db.id,
        description= ticket_input.description,
        quantity= ticket_input.quantity,
        unit_price= registration_order_db.total_amount,
        total_amount= (registration_order_db.total_amount*ticket_input.quantity),
        registration_setup_item_id= ticket_input.registration_setup_item_id,
        code= registration_order_item_type_code
    )
    registration_order_item_db = create_registration_order_item(db, registration_order_item_db)
    template_id = 'tem-cbd6cb4a-fff3-4778-94a4-59b737561cdf'
    template = get_master_template_by_id(db, template_id)
    tickets = []
    for _ in range(ticket_input.quantity):
        new_ticket = create_registration_ticket(db, reg_ticket_schemas.RegistrationTicketCreate(registration_order_item_id=registration_order_item_db.id))
        db.commit()
        tickets.append(new_ticket)
    pdf_ticket = generate_pdf_tickets(db, tickets[0],template, event, registration_order_db, registration_order_item_db, upload=True)
    for ticket in tickets:
        ticket.ticket_url = pdf_ticket['url']
        update_registration_ticket(db, ticket.ticket_id, ticket)
    return tickets

@router.delete('/delete_registration_order_item/{uuid}')
def delete_order_item(uuid: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,])):
    delete_registration_order_item(db, uuid)
    return True

@router.get('/get_orders_items/')
def get_orders_items(db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,])):
    attendee = get_attendees_by_user_id(db, current_user.id)
    if not attendee:
        raise HTTPException(status_code=404, detail='Attendee not found')
    registration_order_items = db.query(RegistrationOrderItemModel).options(
        joinedload(RegistrationOrderItemModel.registration_order),
        joinedload(RegistrationOrderItemModel.registration_ticket),
        joinedload(RegistrationOrderItemModel.registration_order).joinedload(RegistrationOrderModel.conference)  # eager load the related Conference data
    ).filter(
        RegistrationOrderItemModel.registration_order_id == RegistrationOrderModel.id,
        RegistrationOrderModel.attendee_id == attendee.id
    ).all()
    registration_order_items_schemas = [
        create_schema(item, db) for item in registration_order_items
    ]

    return registration_order_items_schemas

@router.get('/get_ticket/{ticket_id}')
def get_ticket(ticket_id: str, db: Session = Depends(get_db),current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,])):
    ticket = get_registration_ticket_by_ticket_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail='Ticket not found')
    registration_order_item = get_registration_order_item_by_id(db, ticket.registration_order_item_id)
    registration_order = get_registration_order_by_id(db, registration_order_item.registration_order_id)
    event_id = registration_order.event_id
    event = get_conference_by_id(db, event_id)
    ticket_data = generate_input_data(db, ticket, event, registration_order, registration_order_item)
    event_dict = conference_to_dict(event)
    event_dict['location'] = event.location
    event_dict['status'] = event.status
    event = ConferenceResponse(**event_dict)
    event.client = None
    event.sponsors = None
    event.exhibitors = None
    registration_order_dict = registration_order.__dict__
    registration_order = RegistrationOrder(**registration_order_dict)
    registration_order_item_dict = registration_order_item.__dict__
    registration_order_item = RegistrationOrderItem(**registration_order_item_dict)
    return {'ticket_data': ticket_data, 'event': event, 'registration_order': registration_order, 'registration_order_item': registration_order_item}

@router.get('/download_ticket/{ticket_id}')
def download_ticket(ticket_id: str, db: Session = Depends(get_db),current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,])):
    ticket = get_registration_ticket_by_ticket_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail='Ticket not found')
    registration_order_item = get_registration_order_item_by_id(db, ticket.registration_order_item_id)
    registration_order = get_registration_order_by_id(db, registration_order_item.registration_order_id)
    event_id = registration_order.event_id
    event = get_conference_by_id(db, event_id)
    # fetch the template from the database
    template_id = 'tem-cbd6cb4a-fff3-4778-94a4-59b737561cdf'
    template = get_master_template_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail='Template not found')
    pdf_stream = generate_pdf_ticket(db,ticket, template, event, registration_order, registration_order_item)
    response = StreamingResponse(pdf_stream, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename={ticket_id}.pdf"
    return response

@router.get('/download_tickets/{ticket_id}')
def download_tickets(ticket_id: str, db: Session = Depends(get_db),current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,])):
    ticket = get_registration_ticket_by_ticket_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail='Ticket not found')
    url = ticket.ticket_url
    response = requests.get(url, stream=True)
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="File not found")
    return StreamingResponse(response.iter_content(chunk_size=1024), media_type='application/pdf', headers={'Content-Disposition': 'attachment; filename=ticket.pdf'})

@router.get('/download_invoice/')
def download_invoice(order_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,])):
    registration_order = get_registration_order_by_order_id(db, order_id)
    if not registration_order:
        raise HTTPException(status_code=404, detail='Order not found')
    event = get_conference_by_id(db, registration_order.event_id)
    attendee = get_an_attendee_by_id(db, registration_order.attendee_id)
    attendee = get_user(db, attendee.user_id)
    if not attendee:
        raise HTTPException(status_code=404, detail='Attendee not found')
    if attendee.id != current_user.id:
        raise HTTPException(status_code=403, detail='Attendee not authorized to view this invoice')
    if not event:
        raise HTTPException(status_code=404, detail='Event not found')
    registration_order_items = get_registration_order_items_by_registration_order_id(db, registration_order.id)
    template_id = 'tem-224f6d50-8f08-41d4-8999-1e4464b343b6'
    template = get_master_template_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail='Template not found')
    pdf_stream = generate_pdf_invoice(db, template, event, registration_order, registration_order_items, attendee)
    response = StreamingResponse(pdf_stream, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename=invoice.pdf"
    return response

@router.post('/generate_report')
def generate_report(report: Report, db: Session = Depends(get_db),current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name])):
    # fetch the template from the database
    template_id = report.template_id
    output_filename = report.output_filename
    input_data = report.input_data
    template = get_template_by_id(db, template_id, current_user.organization_user[0].organization_id)
    if not template:
        raise HTTPException(status_code=404, detail='Template not found')
    # generate the report
    pdf_stream = generate_report_using_template(template, input_data)  
    response = StreamingResponse(pdf_stream, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename={output_filename}.pdf"
    return response

def create_schema(item, db):
    schema = RegistrationOrderItemResponse.from_orm(item)
    schema.registration_order = item.registration_order
    schema.registration_ticket = item.registration_ticket

    if item.registration_ticket is not None:
        registration_order = item.registration_order
        event = registration_order.conference  # use the eagerly loaded data
        ticket_data_list = [
            generate_input_data(db, ticket, event, registration_order, item) for ticket in item.registration_ticket
        ]
        event_dict = conference_to_dict(event)
        event_dict['location'] = event.location
        event_dict['status'] = event.status
        event = ConferenceResponse(**event_dict)
        event.client = None
        event.sponsors = None
        event.exhibitors = None
        schema.event = event
        schema.ticket_data = ticket_data_list

    return schema