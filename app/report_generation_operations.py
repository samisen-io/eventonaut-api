from datetime import date
import io
import json
import os
import tempfile
from fastapi import HTTPException, UploadFile
import requests
import inflect
import pypugjs.ext.jinja
from jinja2 import Environment, FileSystemLoader
from io import BytesIO
from weasyprint import HTML
import qrcode
from app.crud.attendee_crud import get_an_attendee_by_id, get_attendee_by_id
from app.crud.organization_crud import get_organization_by_id
from app.crud.registration_order_crud_temp import get_registration_order_by_id
from app.crud.registration_order_item_crud import get_registration_order_item_by_id
from app.crud.registration_setup_item_crud import get_registration_setup_item
from app.crud.registration_ticket_crud_temp import get_registration_ticket_by_ticket_id, get_registration_tickets_by_registration_order_item_id
from app.crud.users_crud import get_user
from app.models import Conference
from app.routers import upload_image
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter, PdfReader, PdfWriter

def generate_qr_code(ticket_id, event_id):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr_data = {
        "event_id": event_id,
        "ticket_id": ticket_id
    }
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    file = UploadFile(filename=f"qr_code_{ticket_id}.png", file=img_byte_arr)
    result = upload_image.upload_file(file)
    return result['url']

    
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
    with tempfile.NamedTemporaryFile(mode = 'w', encoding='utf-8', delete=False) as temp_file:
        temp_file.write(requests.get(template.template_url).content.decode('utf-8'))
        html = render_pug_template(temp_file.name, input_data)
        pdf_io = BytesIO()
        try:
            pdf = HTML(string=html).write_pdf()
            pdf_io.write(pdf)
            if pdf_io.tell() > 0:
                pdf_io.seek(0)
                return pdf_io
            else:
                raise HTTPException(status_code=500, detail='Error generating report')
        except Exception as e:
            raise HTTPException(status_code=500, detail='Error generating report')

def generate_input_data(db, ticket, event, registration_order, registration_order_item, download=False):
    registration_setup_item = get_registration_setup_item(db, registration_order_item.registration_setup_item_id)
    user = get_user(db, get_an_attendee_by_id(db, registration_order.attendee_id).user_id)
    input_data = {
        'title': get_organization_by_id(db, event.organization_id).name, 
        'event': event.name, 
        'orderNumber': registration_order.order_id,
        'logo': event.conference_banner_url,
        'ticketType': 'General Admission' if registration_setup_item is None else registration_setup_item.name,
        'tickteID': ticket.ticket_id,
        'address': f"{event.venue.name}, {event.venue.address}",
        'dateTime': f"{event.start_date.strftime('%A, %d %B %Y')} to {event.end_date.strftime('%A, %d %B %Y')}",
        'orderType': 'Free Order',
        'customerName': f"{user.first_name} {user.last_name}",
        'orderDate': registration_order.created_on.strftime('%d %B %Y'),
        'orderTime': registration_order.created_on.strftime('%H:%M')
    }
    if download:
        input_data['qrCode'] = generate_qr_code(ticket.ticket_id, event.uuid)
    return input_data

def generate_pdf_ticket(db, ticket, template, event, registration_order, registration_order_item):
    temp_file = download_the_template(template.template_url)
    input_data = generate_input_data(db, ticket, event, registration_order, registration_order_item, True)
    html = render_pug_template(temp_file, input_data)
    pdf_io = BytesIO()
    try:
        pdf = HTML(string=html).write_pdf()
        pdf_io.write(pdf)
        if pdf_io.tell() > 0:
            pdf_io.seek(0)
            os.remove(temp_file)
            return pdf_io
        else:
            raise HTTPException(status_code=500, detail='Error generating ticket')
    except Exception as e:
        os.remove(temp_file)
        raise HTTPException(status_code=500, detail='Error generating ticket')

def generate_pdf_tickets(db, tickets, template, event, upload=False):
    temp_file = download_the_template(template.template_url)
    writer = PdfWriter()
    for ticket in tickets:
        registration_order_item = get_registration_order_item_by_id(db, ticket.registration_order_item_id)
        registration_order = get_registration_order_by_id(db, registration_order_item.registration_order_id)
        ticket_data = generate_input_data(db, ticket, event, registration_order, registration_order_item, True)
        html = render_pug_template(temp_file, ticket_data)
        pdf_io = BytesIO()
        try:
            pdf = HTML(string=html).write_pdf()
            pdf_io.write(pdf)
            if pdf_io.tell() > 0:
                pdf_io.seek(0)
                reader = PdfReader(pdf_io)
                writer.add_page(reader.pages[0])
            else:
                raise HTTPException(status_code=500, detail='Error generating ticket')
        except Exception as e:
            raise HTTPException(status_code=500, detail='Error generating ticket')

    if os.path.exists(temp_file):
        os.remove(temp_file)

    output_pdf_io = BytesIO()
    writer.write(output_pdf_io)

    if upload:
        file = UploadFile(filename=f'usr-{ticket.ticket_id}.pdf', file=output_pdf_io)
        response = upload_image.upload_file(file)
        return response
    else:
        output_pdf_io.seek(0)
        return output_pdf_io

def generate_invoice_input_data(db, event, registration_order, order_items, user):
    p = inflect.engine()
    items = [{'order_item_type': item.code.capitalize(),
              'description': get_registration_setup_item(db, item.registration_setup_item_id).name,
              'quantity': item.quantity,
              'price': item.unit_price,
              'amount': item.total_amount} for item in order_items]
    organization = get_organization_by_id(db, event.organization_id)
    company_address = organization.address or 'Address Not Provided'
    logo = organization.logo_image_url or 'https://conferencebuddydev.blob.core.windows.net/temporary-images/dyn-6208be2d-cc2e-4581-a4b5-c20b505e4142-default_organization.png'
    return {
        'logo': logo,
        'company_name': organization.name,
        'company_address': company_address,
        'customer_name': (user.first_name + ' ' + user.last_name).title(),
        'customer_email': user.email,
        'date_issued': date.today().strftime("%d %B %Y"),
        'invoice_number': registration_order.order_id,
        'items': items,
        'subtotal': registration_order.amount,
        'tax': registration_order.tax_amount,
        'fee': registration_order.fee_amount,
        'total': registration_order.total_amount,
        'total_in_words': p.number_to_words(registration_order.total_amount)
    }
        
def generate_pdf_invoice(db, template, event, registration_order, order_items, user):
    temp_file = download_the_template(template.template_url)
    invoice_input_data = generate_invoice_input_data(db, event, registration_order, order_items, user)
    html = render_pug_template(temp_file, invoice_input_data)
    pdf_io = BytesIO()
    try:
        pdf = HTML(string=html).write_pdf()
        pdf_io.write(pdf)
        if pdf_io.tell() > 0:
            pdf_io.seek(0)
            os.remove(temp_file)
            return pdf_io
        else:
            raise HTTPException(status_code=500, detail='Error generating invoice')
    except Exception as e:
        os.remove(temp_file)
        raise HTTPException(status_code=500, detail='Error generating invoice')
            