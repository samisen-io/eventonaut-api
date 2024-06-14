import json
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.crud.registration_order_crud import registration_order_item_mapper, registration_order_mapper, create_db_order, get_registration_order, deduct_tickets_from_available_quantity, add_tickets
from ..dependencies import get_db
import uuid
from ..crud import redis_crud, conferences_crud, attendee_crud, registration_setup_crud
import logging
from ..schemas.registration_setup_schemas import RegistrationSetupResponse
from ..schemas.attendee_schemas import Attendee, AttendeeCreate, AttendeeUpdate
from ..schemas.checkout_schemas import CheckoutRequest, CheckoutResponse, Details, CreateOrderRequest, ConfirmOrderRequest, OrderResponse
from email_validator import validate_email, EmailNotValidError
from ..crud.checkout_crud import check_for_extra_tickets, verify_ticket_types, available_tickets_for_event
from ..basicauth import basic_auth
from ..static_enums.payment_status import PaymentStatus
from ..schemas.ticket_checkin_schemas import Ticket
import os
import razorpay
from ..crud import razorpay as razorpay_crud

router = APIRouter(tags=["checkout"])

razorpay_key_id = os.getenv("RAZORPAY_KEY_ID")
razorpay_key_secret = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))

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
    response = CheckoutResponse(session_id=session_id, event_id=conference.uuid, expiration_timestamp=expiration_timestamp)
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
    attendee = attendee_crud.get_attendee_by_email(db, details.email)
    if not attendee:
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

@router.post("/checkout/create-order", response_model=OrderResponse)
async def create_order(create_order_request: CreateOrderRequest, db: Session = Depends(get_db), user = Depends(basic_auth)):
    conference = conferences_crud.get_conference(db, create_order_request.event_id)
    if conference is None:
        logging.exception(f"Conference {create_order_request.event_id} not found")
        raise HTTPException(status_code=404, detail=f"Conference {create_order_request.event_id} not found")
    session_bytes = redis_crud.get_session_from_redis(create_order_request.session_id)
    if session_bytes is None:
        redis_crud.remove_session_from_list(create_order_request.event_id, create_order_request.session_id)
        raise HTTPException(status_code=404, detail=f"Session {create_order_request.session_id} not found")
    session = json.loads(session_bytes)
    reg_setup = registration_setup_crud.get_setup_details(db, conference.id)
    registration_order = registration_order_mapper(reg_setup, session, session["attendee_id"])
    registration_order_items = registration_order_item_mapper(reg_setup.registration_setup_items, session)
    
    razorpay_order = {
        "amount": int(registration_order.total_amount * 100),
        "currency": "INR",
        "receipt": registration_order.uuid
    }
    
    razorpay_order_response = razorpay_crud.create_order(razorpay_client, razorpay_order)
    create_db_order(db, registration_order, registration_order_items, razorpay_order_response["id"])
    response = OrderResponse(message="Order created successfully", event_id=conference.uuid, session_id=create_order_request.session_id, order_id=razorpay_order_response["id"], amount=registration_order.total_amount, currency=razorpay_order["currency"], receipt=razorpay_order["receipt"], payment_status=PaymentStatus.UNPAID)
    return response

@router.post("/checkout/confirm-order", response_model=list[Ticket])
async def confirm_order(confirm_order_request: ConfirmOrderRequest, db: Session = Depends(get_db), user = Depends(basic_auth)):
    conference = conferences_crud.get_conference(db, confirm_order_request.event_id)
    if conference is None:
        logging.exception(f"Conference {confirm_order_request.event_id} not found")
        raise HTTPException(status_code=404, detail=f"Conference {confirm_order_request.event_id} not found")
    session_bytes = redis_crud.get_session_from_redis(confirm_order_request.session_id)
    if session_bytes is None:
        redis_crud.remove_session_from_list(confirm_order_request.event_id, confirm_order_request.session_id)
        raise HTTPException(status_code=404, detail=f"Session {confirm_order_request.session_id} not found")
    session = json.loads(session_bytes)
    reg_order = get_registration_order(db, conference.id, confirm_order_request.order_id, session["attendee_id"])
    if reg_order is None:
        raise HTTPException(status_code=404, detail=f"Order {confirm_order_request.order_id} not found")
    reg_setup = registration_setup_crud.get_setup_details(db, conference.id)
    
    # is_valid = razorpay_crud.verify_payment(order_id=confirm_order_request.order_id, payment_id=confirm_order_request.payment_id, 
    # razorpay_signature=confirm_order_request.signature, razorpay_key_secret=razorpay_key_secret)
    # if not is_valid:
    #     raise HTTPException(status_code=400, detail="Invalid payment")
    # razorpay_crud.capture_payment(razorpay_client, confirm_order_request.payment_id, reg_order.total_amount)
    
    deduct_tickets_from_available_quantity(db, reg_setup, session)
    reg_order.payment_status = PaymentStatus.PAID.value
    db.commit()
    tickets = add_tickets(db, reg_order, conference.uuid)
    redis_crud.delete_data_from_redis(confirm_order_request.session_id)
    redis_crud.remove_session_from_list(confirm_order_request.event_id, confirm_order_request.session_id)
    return tickets

# @router.get("/fill-uuids")
# def fill(db: Session = Depends(get_db)):
#     tickets = db.query(models.RegistrationTicket).all()
#     for ticket in tickets:
#         ticket.uuid = f"tkt-{uuid.uuid4()}"
#         db.add(ticket)
#     db.commit()
#     return {"message": "UUIDs filled successfully"}

# @router.get("/update-ticket_ids")
# def update_ticket_ids(db: Session = Depends(get_db)):
#     tickets = db.query(models.RegistrationTicket).options(joinedload(models.RegistrationTicket.registration_order_item).joinedload(models.RegistrationOrderItem.registration_order)).all()
#     for ticket in tickets:
#         event = db.query(models.Conference).filter(models.Conference.id == ticket.registration_order_item.registration_order.event_id).first()
#         event_id = event.uuid[4:9]
#         order_id = ticket.registration_order_item.registration_order.uuid[4:7]
#         ticket_id = str(ticket.id)
#         if len(ticket_id) == 1:
#             ticket_id = ticket_id.zfill(2)
#         else:
#             ticket_id = ticket_id[-2:]
#         ticket.ticket_id = f"tk-{event_id}-{order_id}-{ticket_id}"
#         db.add(ticket)
#     db.commit()
#     return {"message": "Ticket IDs updated successfully"}
    