from fastapi import APIRouter, Depends

from app.schemas.report_schemas import Report
from ..dependencies import get_db
from app.models import Session


router = APIRouter(tags = ['reports'])

@router.put('/generate_report')
def generate_report(report: Report, db: Session = Depends(get_db)):
    # fetch the template from the database
    template_id = report.template_id
    output_filename = report.output_filename
    input_data = report.input_data
    # template = db.query(Session).filter(Session.id == template_id).first()
    # if not template:
    #     return {'message': 'Template not found'}
    # generate the report
    # report = generate_report_using_template(template, input_data, output_filename)    
    return {'message': 'Report generated successfully'}