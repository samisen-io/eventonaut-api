from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.responses import StreamingResponse

from app.code_generator import generate_unique_string
from app.crud.attendee_crud import get_attendee_by_email, get_attendees_by_user_id
from app.crud.conferences_crud import get_conference, get_conference_by_conference_uuid, get_conference_by_id, get_conference_by_uuid
from app.crud.master_template_crud import get_master_template_by_id
from app.crud.registration_order_crud_temp import create_registration_order, get_registration_order_by_id
from app.crud.registration_order_item_crud import create_registration_order_item, get_registration_order_item_by_id
from app.crud.registration_order_item_type_crud_temp import get_registration_order_item_type_by_id
from app.crud.registration_ticket_crud_temp import create_registration_ticket, get_registration_ticket_by_ticket_id
from app.schemas import registration_ticket_schema_temp as reg_ticket_schemas
from app.schemas import ticket_schema_temp as ticket_schemas
from app.crud.template_crud import get_template_by_id
from app.oauth2 import get_current_active_user
from app.report_generation_operations import generate_input_data, generate_pdf_ticket, generate_report_using_template
from app.schemas.client_schemas import ClientResponse
from app.schemas.conference_schemas import ConferenceResponse
from app.schemas.exhibitor_schemas import ExhibitorResponse
from app.schemas.registration_order_item_schema_temp import RegistrationOrderItem, RegistrationOrderItemCreate
from app.schemas.registration_order_schema_temp import RegistrationOrder, RegistrationOrderCreate
from app.schemas.report_schemas import Report
from app.schemas.user_schemas import User
from app.schemas.venue_schemas import VenueResponse
from app.static_enums.role import RoleEnum
from ..dependencies import get_db
from app.models import Session


router = APIRouter(tags = ['reports'])

@router.post('/create_ticket')
def create_ticket(ticket_input: ticket_schemas.CreateTicket, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,])):
    print(ticket_input)
    current_user_id = current_user.id
    attendee = get_attendees_by_user_id(db, current_user_id)
    event = get_conference_by_conference_uuid(db, ticket_input.event_id)
    print(attendee.id)
    registration_order_db = RegistrationOrderCreate(
        event_id=event.id,
        attendee_id=attendee.id,
        amount=ticket_input.amount,
        tax_amount=ticket_input.tax_amount,
        fee_amount=ticket_input.fee_amount,
    )
    registration_order_db = create_registration_order(db,registration_order_db)
    # get the registration order id
    registration_order_id = registration_order_db.id
    print(registration_order_id)
    registration_order_item_type_code = get_registration_order_item_type_by_id(db, ticket_input.type).code
    registration_order_item_db = RegistrationOrderItemCreate(
        registration_order_id= registration_order_id,
        description= ticket_input.description,
        quantity= ticket_input.quantity,
        unit_price= registration_order_db.total_amount,
        total_amount= (registration_order_db.total_amount*ticket_input.quantity),
        type= ticket_input.type,
        code= registration_order_item_type_code
    )
    registration_order_item_db = create_registration_order_item(db, registration_order_item_db)
    # create a registration ticket
    ticket = reg_ticket_schemas.RegistrationTicketCreate(
        registration_order_item_id=registration_order_item_db.id
    )
    return create_registration_ticket(db, ticket)

@router.get('/get_ticket/{ticket_id}')
def get_ticket(ticket_id: str, db: Session = Depends(get_db),current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,])):
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
    ticket_data = generate_input_data(db,ticket_id, template, event, registration_order)
    venue_response = VenueResponse(**event.venue.__dict__)
    event_dict = event.__dict__
    event_dict['venue'] = venue_response
    event_dict['location'] = event.location
    event_dict['status'] = event.status
    client_dict = event.client.__dict__
    if 'status' not in client_dict:
        client_dict['status'] = 'default_status'  # replace 'default_status' with the actual default status
    event_dict['client'] = ClientResponse(**client_dict)
    event_dict['exhibitors'] = [ExhibitorResponse(**exhibitor.__dict__) for exhibitor in event.exhibitors]
    event = ConferenceResponse(**event_dict)
    registration_order_dict = registration_order.__dict__
    # if '_sa_instance_state' in registration_order_dict:
    #     del registration_order_dict['_sa_instance_state']
    registration_order = RegistrationOrder(**registration_order_dict)
    registration_order_item_dict = registration_order_item.__dict__
    # if '_sa_instance_state' in registration_order_item_dict:
    #     del registration_order_item_dict['_sa_instance_state']
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
    pdf_stream = generate_pdf_ticket(db,ticket_id, template, event, registration_order)
    response = StreamingResponse(pdf_stream, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename={ticket_id}.pdf"
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