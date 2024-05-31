from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.responses import StreamingResponse

from app.crud.template_crud import get_template_by_id
from app.oauth2 import get_current_active_user
from app.report_generation_operations import generate_report_using_template, generate_ticket_using_template
from app.schemas.report_schemas import Report
from app.schemas.user_schemas import User
from app.static_enums.role import RoleEnum
from ..dependencies import get_db
from app.models import Session


router = APIRouter(tags = ['reports'])

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

@router.post('/generate_ticket')
def generate_ticket(ticket_id: str, db: Session = Depends(get_db),current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name])):
    # fetch the template from the database
    template_id = 'tem-eb7daf3f-2ef4-46fa-ac6f-1d3ea23a40d7'
    template = get_template_by_id(db, template_id, current_user.organization_user[0].organization_id)
    if not template:
        raise HTTPException(status_code=404, detail='Template not found')
    pdf_stream = generate_ticket_using_template(ticket_id, template)
    response = StreamingResponse(pdf_stream, media_type="application/pdf")
    response.headers["Content-Disposition"] = f"attachment; filename=ticket_{ticket_id}.pdf"
    return response