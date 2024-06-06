import json
import os
import redis
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from ..dependencies import get_db
import uuid
from ..crud import redis_crud, conferences_crud, attendee_crud
import logging
from ..schemas.registration_setup_schemas import RegistrationSetupResponse
from ..schemas.attendee_schemas import Attendee, AttendeeCreate, AttendeeUpdate
from ..schemas.checkout_schemas import CheckoutRequest, CheckoutResponse, Details
from email_validator import validate_email, EmailNotValidError
from ..crud.checkout_crud import check_for_extra_tickets, verify_ticket_types, available_tickets_for_event
from ..basicauth import basic_auth

router = APIRouter(tags=["checkout"])

@router.get("/get-all-available-tickets/{event_id}", response_model=RegistrationSetupResponse)
async def get_all_available_tickets(event_id: str, db: Session = Depends(get_db), user = Depends(basic_auth)):
    try:
        conference = conferences_crud.get_conference(db, event_id)
        if conference is None:
            logging.exception(f"Conference {event_id} not found")
            raise HTTPException(status_code=404, detail=f"Conference {event_id} not found")
        return available_tickets_for_event(db, conference)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(checkout_request: CheckoutRequest, db: Session = Depends(get_db), user = Depends(basic_auth)):
    conference = conferences_crud.get_conference(db, checkout_request.event_id)
    if conference is None:
        logging.exception(f"Conference {checkout_request.event_id} not found")
        raise HTTPException(status_code=404, detail=f"Conference {checkout_request.event_id} not found")
    avalibale_tickets = available_tickets_for_event(db, conference)
    verify_ticket_types(checkout_request, avalibale_tickets)
    check_for_extra_tickets(checkout_request, avalibale_tickets)
    session_id = f"tkt-ses-{uuid.uuid4().hex}"
    checkout_request_dict = checkout_request.model_dump()
    checkout_request_dict["event_id"] = conference.id
    checkout_request_dict["attendee_id"] = None
    expiration_timestamp = redis_crud.save_session_to_redis(session_id, checkout_request_dict)
    redis_crud.save_list_of_sessions_to_redis(conference.uuid, session_id)
    response = CheckoutResponse(session_id=session_id, expiration_timestamp=expiration_timestamp)
    return response

@router.post("/checkout/details", response_model=Attendee)
async def checkout_details(details: Details, db: Session = Depends(get_db), user = Depends(basic_auth)):
    try:
        valid = validate_email(details.email)
        details.email = valid.normalized.lower()
    except EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    session_bytes = redis_crud.get_session_from_redis(details.session_id)
    if session_bytes is None:
        redis_crud.remove_session_from_list(details.event_id, details.session_id)
        raise HTTPException(status_code=404, detail=f"Session {details.session_id} not found")
    session = json.loads(session_bytes)
    attendee = attendee_crud.create_attendee(db, AttendeeCreate(email=details.email, hashed_password=uuid.uuid1().hex[:16]))
    attendee = attendee_crud.update_attendee_by_uuid(db, attendee.user_id, AttendeeUpdate(first_name=details.first_name, last_name=details.last_name))
    session["attendee_id"] = attendee.id
    redis_crud.update_session_in_redis(details.session_id, session)
    return attendee

@router.delete("/checkout/{session_id}")
async def delete_checkout(session_id: str, user = Depends(basic_auth)):
    value = redis_crud.delete_data_from_redis(session_id)
    if value == 0:
        raise HTTPException(status_code=404, detail=f"Session {session_id} expired")
    return {"message": f"Session {session_id} deleted"}