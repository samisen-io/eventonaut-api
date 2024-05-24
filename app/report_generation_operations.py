import os
import tempfile
from fastapi import HTTPException
import requests
import pdfkit
import pypugjs.ext.jinja
from jinja2 import Environment, FileSystemLoader
from pdf_reports import pug_to_html
from weasyprint import HTML
from io import BytesIO

def render_pug_template(template_path, context):
    template_dir, template_name = os.path.split(template_path)
    env = Environment(loader = FileSystemLoader(template_dir), extensions=['pypugjs.ext.jinja.PyPugJSExtension'])
    template = env.get_template(template_name)
    return template.render(context)

def generate_report_using_template(template, input_data):
    template_url = template.template_url
    response = requests.get(template_url)
    with tempfile.NamedTemporaryFile(mode = 'w', encoding='utf-8', delete=False) as temp_file:
        temp_file.write(response.content.decode('utf-8'))
    html = render_pug_template(temp_file.name, input_data)
    pdf_io = BytesIO()
    try:
        HTML(string=html).write_pdf(pdf_io)
        if pdf_io.tell() > 0:
            pdf_io.seek(0)
            os.remove(temp_file.name)
            return pdf_io
        else:
            raise HTTPException(status_code=500, detail='Error generating report')
    except Exception as e:
        os.remove(temp_file.name)
        raise HTTPException(status_code=500, detail='Error generating report')