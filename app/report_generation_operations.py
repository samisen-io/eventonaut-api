import os
import tempfile
from fastapi import HTTPException
import requests
import pypugjs.ext.jinja
from jinja2 import Environment, FileSystemLoader
from io import BytesIO
from weasyprint import HTML

from app.crud.attendee_crud import get_an_attendee_by_id, get_attendee_by_id
from app.crud.organization_crud import get_organization_by_id
from app.crud.users_crud import get_user


def render_pug_template(template_path, context):
    template_dir, template_name = os.path.split(template_path)
    env = Environment(loader = FileSystemLoader(template_dir), extensions=['pypugjs.ext.jinja.PyPugJSExtension'])
    template = env.get_template(template_name)
    return template.render(context)

def download_the_template(template_url):
    response = requests.get(template_url)
    with tempfile.NamedTemporaryFile(mode = 'w', encoding='utf-8', delete=False) as temp_file:
        temp_file.write(response.content.decode('utf-8'))
    return temp_file.name

def generate_report_using_template(template, input_data):
    temp_file = download_the_template(template.template_url)
    html = render_pug_template(temp_file.name, input_data)
    pdf_io = BytesIO()
    try:
        pdf = HTML(string=html).write_pdf()
        pdf_io.write(pdf)
        if pdf_io.tell() > 0:
            pdf_io.seek(0)
            os.remove(temp_file.name)
            return pdf_io
        else:
            raise HTTPException(status_code=500, detail='Error generating report')
    except Exception as e:
        os.remove(temp_file.name)
        raise HTTPException(status_code=500, detail='Error generating report')
    
def generate_input_data(db, ticket_id, template, event, registration_order):
    organization_id = event.organization_id
    organization = get_organization_by_id(db, organization_id)
    venue = event.venue
    address = venue.name + ', ' + venue.address
    date = event.start_date.strftime('%A, %d %B %Y')+' to '+event.end_date.strftime('%A, %d %B %Y')
    attendee_id = registration_order.attendee_id
    attendee = get_an_attendee_by_id(db, attendee_id)
    user_id = attendee.user_id
    user = get_user(db, user_id)
    user_name = user.first_name + ' ' + user.last_name
    order_date = registration_order.created_on.strftime('%d %B %Y')
    order_time = registration_order.created_on.strftime('%H:%M')

    input_data = {
        'title': organization.name, 
        'event': event.name, 
        'orderNumber': registration_order.order_id,
        'logo': event.conference_banner_url,
        'ticketType': 'General Admission',
        'address': address,
        'dateTime': date,
        'orderType': 'Free Order',
        'customerName': user_name,
        'orderDate': order_date,
        'orderTime': order_time,
        'qrCode': 'https://conferencebuddydev.blob.core.windows.net/temporary-images/dyn-07d92fac-a59f-42c8-9e75-b53f43a0410d-conf_qrcode.png'
    }
    return input_data

def generate_pdf_ticket(db, ticket_id, template, event, registration_order):
    temp_file = download_the_template(template.template_url)
    input_data = generate_input_data(db, ticket_id, template, event, registration_order)
    html = render_pug_template(temp_file, input_data)
    pdf_io = BytesIO()
    try:
        pdf = HTML(string=html).write_pdf()
        pdf_io.write(pdf)
        if pdf_io.tell() > 0:
            pdf_io.seek(0)
            os.remove(temp_file)
            return input_data, pdf_io
        else:
            raise HTTPException(status_code=500, detail='Error generating ticket')
    except Exception as e:
        os.remove(temp_file)
        raise HTTPException(status_code=500, detail='Error generating ticket')