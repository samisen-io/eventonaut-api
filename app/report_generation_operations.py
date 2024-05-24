import os
import tempfile
from fastapi import HTTPException
import requests
import pypugjs.ext.jinja
from jinja2 import Environment, FileSystemLoader
from io import BytesIO
import pdfkit
# os.environ['WEASYPRINT_DLL_DIRECTORIES']=r'C:\Program Files\GTK3-Runtime Win64\bin'
# os.environ['WEASYPRINT_DLL_DIRECTORIES']=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "GTK3-Runtime Win64", "bin")
# print(os.environ['WEASYPRINT_DLL_DIRECTORIES'])
# from weasyprint import HTML

path_wkhtmltopdf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"wkhtmltopdf", "wkhtmltopdf.exe")
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)


# os.environ['WEASYPRINT_DLL_DIRECTORIES']=r'C:\Program Files\GTK3-Runtime Win64\bin'
os.environ['WEASYPRINT_DLL_DIRECTORIES']=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "GTK3-Runtime Win64", "bin")
print(os.environ['WEASYPRINT_DLL_DIRECTORIES'])
from weasyprint import HTML


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
        pdf = pdfkit.from_string(html, False)
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