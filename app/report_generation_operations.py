import os
import tempfile
from fastapi import HTTPException
import requests
import pypugjs.ext.jinja
from jinja2 import Environment, FileSystemLoader
from io import BytesIO
from weasyprint import HTML

from app.schemas import ticket_input_schemas


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
    
def generate_ticket_using_template(ticket_id, template):
    temp_file = download_the_template(template.template_url)
    # fetch the input fromthe database
    print(f"Generating ticket for ticket_id: {ticket_id}")
    input_data = {
        'title': 'eventbrite', 
        'event': 'Eventonaut Customer Conference 1', 
        'orderNumber': '1234567890',
        'logo': 'https://conferencebuddydev.blob.core.windows.net/temporary-images/dyn-14341489-b31e-42f7-88a6-5a3788e012cc-doggo.png',
        'ticketType': 'General Admission',
        'address': 'Awfis, Lorven Tiara, Awfis, Lorven Tiara, Kondapur 500084, India',
        'dateTime': 'Saturday, 25 May 2024 from 10:00 to 12:00 (IST)',
        'orderType': 'Free Order',
        'customerName': 'Martin S',
        'orderDate': '17 May 2024',
        'orderTime': '12:40',
        'qrCode': 'https://conferencebuddydev.blob.core.windows.net/temporary-images/dyn-07d92fac-a59f-42c8-9e75-b53f43a0410d-conf_qrcode.png'
    }
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