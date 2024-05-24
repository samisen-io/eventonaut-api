import tempfile
from fastapi import requests
import pdfkit
import pypugjs.ext.jinja
from pdf_reports import pug_to_html

def generate_report_using_template(template, input_data, output_filename):
    response = requests.get(template)
    response.raise_for_status()
    
    with tempfile.NamedTemporaryFile(delete=False, encoding='utf-8') as temp_file:
        temp_file.write(response.content)
    html = pug_to_html(temp_file.name)
    return ''