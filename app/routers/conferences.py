from fastapi import APIRouter, HTTPException, Depends, Security, status
import logging
from fastapi.responses import StreamingResponse
import sqlalchemy
from sqlalchemy.orm import Session
from app import models
from app.schemas.user_schemas import UserAuthentication as User
from app.oauth2 import get_current_active_organization, get_current_active_user
from app.static_enums.role import RoleEnum
from ..static_enums import event_types
from ..schemas import conference_schemas as schemas
from ..crud import conferences_crud as crud, users_crud, client_crud, venue_crud, sponsors_crud, exhibitor_crud
from ..schemas.organization_schemas import OrganizationSecurity
from ..dependencies import get_db
from .. import basicauth
from datetime import date
import qrcode
import io
import json

router = APIRouter(tags=["conferences"])

@router.post("/conferences", response_model=schemas.ConferenceResponse, status_code=status.HTTP_201_CREATED)
def create_conference_for_user(conference: schemas.ConferenceCreate, db: Session = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name,"organizer"])):
    db_venue = venue_crud.get_venue_by_id_for_organization(db, venue_id=conference.venue_id, organization_id=current_organization.id)
    if db_venue is None:
        logging.exception("Venue not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    if conference.client_id is not None:
        db_client = client_crud.get_client_by_uuid_and_organization_id(db, client_id=conference.client_id, organization_id=current_organization.id)
        if not db_client:
            logging.exception("Client not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    if conference.start_date > conference.end_date or conference.start_date < date.today():
        logging.exception("Invalid date range")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date range")
    sponsors_ids = []
    if conference.sponsor_ids is not None and len(conference.sponsor_ids) > 0:
        for sponsor_id in conference.sponsor_ids:
            db_sponsor = sponsors_crud.get_sponsor_by_uuid(db, uuid=sponsor_id, organization_id=current_organization.id)
            if not db_sponsor:
                logging.exception("Sponsor not found")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsor not found")
            if db_sponsor.id not in sponsors_ids:
                sponsors_ids.append(db_sponsor.id)
    exhibitor_ids = []
    if conference.event_type.upper() == event_types.EventTypeEnum.CONFERENCE.name and conference.exhibitor_ids is not None:
        logging.exception("Exhibitors not allowed for type conference")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Exhibitors not allowed for type conference")
    elif conference.event_type.upper() == event_types.EventTypeEnum.TRADESHOW.name and conference.exhibitor_ids is not None:
        for exhibitor_id in conference.exhibitor_ids:
            db_exhibitor = exhibitor_crud.get_exhibitor_by_id(db, exhibitor_id, current_organization.id)
            if not db_exhibitor:
                logging.exception("Exhibitor not found")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibitor not found")
            if db_exhibitor.id not in exhibitor_ids:
                exhibitor_ids.append(db_exhibitor.id)
    db_conference = crud.create_user_conference(db=db, conference=conference, organization_id=current_organization.id, venue_id=db_venue.id, sponsor_ids=sponsors_ids, exhibitor_ids=exhibitor_ids, client_id = db_client.id if conference.client_id else None)
    logging.info("Conference created: " + db_conference.uuid)
    conference_response = schemas.ConferenceResponse(**db_conference.__dict__)
    save_audit_log(db, "create", "conferences", current_organization.id, None, None, conference_response)
    return db_conference 

@router.get("/conferences/all_conferences", response_model=list[schemas.ConferenceResponse])
def get_all_conferences(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if offset < 0 or limit < 0:
        logging.exception("Invalid offset or limit")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid query parameters")
    conferences = crud.get_all_conferences(db, offset=offset, limit=limit)
    if conferences is None or len(conferences) == 0:
        logging.exception("No conferences found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    logging.info("All Conferences retrieved")
    return conferences

# @router.get("/conferences/by_organization", response_model=list[schemas.ConferenceResponse])
# def get_all_conferences_by_organization_id(offset: int = 0, limit: int = 100, db: Session = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name])):
#     db_conferences = crud.get_all_conferences_by_organization_id(db, organization_id = current_organization.id, offset=offset, limit=limit)
#     if db_conferences is None or len(db_conferences) == 0:
#         logging.exception("No conferences found")
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
#     logging.info(f"Conferences retrieved for Organization id: {current_organization.uuid}")
#     return db_conferences

@router.get("/conferences/for_attendee", response_model=list[schemas.ConferenceResponse])
def get_all_conferences_for_attendee(offset: int = 0, limit: int = 100, db: Session = Depends(get_db),basic_auth = Depends(basicauth.basic_auth)):
    if offset < 0 or limit < 0:
        logging.exception("Invalid offset or limit")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid query parameters")
    conferences = crud.get_all_conferences_for_attendee(db, offset=offset, limit=limit)
    if conferences is None or len(conferences) == 0:
        logging.exception("No conferences found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    logging.info("Conferences retrieved for attendee")
    return conferences

@router.get("/conferences", response_model=list[schemas.ConferenceResponse])
def get_all_conferences_by_organization_id(offset: int = 0, limit: int = 10, db: Session = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name,"organizer"])):
    db_conferences = crud.get_conferences_by_organization_id(db, organization_id=current_organization.id, offset=offset, limit=limit)
    if db_conferences is None or len(db_conferences) == 0:
        logging.exception("No conferences found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    logging.info("Conferences retrieved for organization: " + current_organization.uuid)
    return db_conferences

@router.put("/conferences", response_model=schemas.ConferenceResponse)
def update_conference(conference: schemas.ConferenceUpdate, db: Session = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    conference_dict = conference.model_dump()
    conference_dict.pop("id")
    if all(value is None for value in conference_dict.values()):
        logging.exception("Invalid request body")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid request body")
    db_conference = crud.get_conference_by_uuid(db, uuid=conference.id, organization_id=current_organization.id)
    if db_conference is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    if conference.venue_id is not None:
        db_venue = venue_crud.get_venue_by_id_for_organization(db, venue_id=conference.venue_id, organization_id=current_organization.id)
        if db_venue is None:
            logging.exception("Venue not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venue not found")
    if conference.start_date is not None and conference.end_date is not None:
        if conference.start_date > conference.end_date or conference.start_date < date.today():
            logging.exception("Invalid date range")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date range")
    if conference.client_id is not None:
        if not client_crud.get_client_by_uuid_and_organization_id(db, client_id=conference.client_id, organization_id=current_organization.id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    sponsors_ids = []
    if conference.sponsor_ids is not None and len(conference.sponsor_ids) > 0:
        for sponsor_id in conference.sponsor_ids:
            db_sponsor = sponsors_crud.get_sponsor_by_uuid(db, uuid=sponsor_id, organization_id=current_organization.id)
            if not db_sponsor:
                logging.exception("Sponsor not found")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sponsor not found")
            if db_sponsor.id not in sponsors_ids:
                sponsors_ids.append(db_sponsor.id)
    exhibitors_ids = []
    if (conference.event_type and conference.event_type.upper() == event_types.EventTypeEnum.CONFERENCE.name and conference.exhibitor_ids is not None) or (not conference.event_type and db_conference.event_type.upper() == event_types.EventTypeEnum.CONFERENCE.name and conference.exhibitor_ids is not None):
        logging.exception("Exhibitors not allowed for type conference")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Exhibitors not allowed for type conference")
    if (conference.event_type and conference.event_type.upper() == event_types.EventTypeEnum.TRADESHOW.name and conference.exhibitor_ids is not None) or (not conference.event_type and db_conference.event_type.upper() == event_types.EventTypeEnum.TRADESHOW.name and conference.exhibitor_ids is not None):
        if conference.exhibitor_ids is not None and len(conference.exhibitor_ids) > 0:
            for exhibitor_id in conference.exhibitor_ids:
                db_exhibitor = exhibitor_crud.get_exhibitor_by_id(db, exhibitor_id, current_organization.id)
                if not db_exhibitor:
                    logging.exception("Exhibitor not found")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exhibitor not found")
                if db_exhibitor.id not in exhibitors_ids:
                    exhibitors_ids.append(db_exhibitor.id)
    updated_conference = crud.update_user_conference(db=db, conference=conference, db_conference=db_conference, sponsor_ids=sponsors_ids,exhibitor_ids=exhibitors_ids)
    logging.info("Conference updated: " + updated_conference.uuid)
    save_audit_log(db, "update", "confereces", current_organization.id, None, None, updated_conference)
    return updated_conference

@router.delete("/conferences/{conference_id}")
def delete_conference_organization_id_conference_id(conference_id: str, db: Session = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    db_conference = crud.get_conference_by_uuid(db,organization_id=current_organization.id, uuid=conference_id)
    if db_conference is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    deleted_conference = crud.delete_conference(db=db, conference=db_conference)
    logging.info("Conference deleted: " + db_conference.uuid)
    save_audit_log(db, "delete", "conferences", current_organization.id, None, db_conference, None)
    return deleted_conference

@router.get("/conferences/generate_qr_code/{conference_id}")
def generate_qr_code(conference_id: str, db: Session = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    conference = crud.get_conference_by_uuid(db, uuid=conference_id, organization_id=current_organization.id)
    if conference is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr_data = {
        "conference_id": conference.uuid,
        "conference_name": conference.name,
        "conference_code": conference.code
    }

    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr)
    img_byte_arr.seek(0)

    headers = {
        "Content-Disposition": f"attachment; filename=conf_qrcode.png",
    }

    logging.info("QR code generated: " + conference.name)
    return StreamingResponse(img_byte_arr, media_type="image/png", headers=headers)

@router.get("/conferences/{conference_id}", response_model=schemas.ConferenceResponse)
def get_conference_by_conference_id(conference_id: str, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):    
    conference = crud.get_conference_by_conference_uuid(db, uuid=conference_id)
    if conference is None:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    logging.info("Conference retrieved: " + conference.uuid)
    return conference

@router.get("/event-list-summary", response_model=schemas.ConferenceListSummary)
def get_conference_list_summary(db: Session = Depends(get_db), current_organization: OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    try:
        conference_list_summary = crud.get_event_list_summary(db, current_organization.id)
        logging.info("Conference list summary retrieved for owner id: " + current_organization.uuid)
        return conference_list_summary
    except Exception as e:
        logging.exception("Error retrieving conference list summary" + str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error retrieving conference list summary" + str(e))

def save_audit_log(db, operation, table, organization_id, user_id=None, old_value=None, new_value=None):
    print(f"user_id: {user_id} of organization {organization_id} performed {operation} on a {table} table. old value: {old_value}, new value: {new_value}")