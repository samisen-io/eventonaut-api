from datetime import datetime
import json
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.crud.master_template_crud import get_master_template_by_id
from app.crud.registration_order_crud import registration_order_item_mapper, registration_order_mapper, create_db_order, get_registration_order, deduct_tickets_from_available_quantity, add_tickets
from app.crud.registration_order_crud_temp import get_registration_order_by_id
from app.crud.registration_order_item_crud import get_registration_order_item_by_id
from app.crud.registration_ticket_crud_temp import get_registration_ticket_by_ticket_id, get_tickets_by_attendee_id_and_event_id, update_registration_ticket
from app.report_generation_operations import generate_pdf_tickets
from ..dependencies import get_db
import uuid
from ..crud import redis_crud, conferences_crud, attendee_crud, registration_setup_crud, transaction_crud
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
from ..static_enums import transaction_types as t_type, transaction_methods as t_method
import logging
from ..otp_generator import send_tickets

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
        logging.info(f"Got tickets for conference {event_id}")
        return available_tickets_for_event(db, conference)
    except HTTPException as e:
        logging.exception(str(e))
        raise e
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(checkout_request: CheckoutRequest, db: Session = Depends(get_db), user = Depends(basic_auth)):
    try:
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
        logging.info(f"Checkout session {session_id} created for conference {conference.uuid}")
        return response
    except HTTPException as e:
        logging.exception(str(e))
        raise e
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkout/details", response_model=Attendee)
async def checkout_details(details: Details, db: Session = Depends(get_db), user = Depends(basic_auth)):
    try:
        try:
            valid = validate_email(details.email)
            details.email = valid.normalized.lower()
        except EmailNotValidError as e:
            logging.exception(str(e))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        session_bytes = redis_crud.get_session_from_redis(details.session_id)
        if session_bytes is None:
            redis_crud.remove_session_from_list(details.event_id, details.session_id)
            logging.exception(f"Session {details.session_id} not found")
            raise HTTPException(status_code=404, detail=f"Session {details.session_id} not found")
        session = json.loads(session_bytes)
        attendee = attendee_crud.get_attendee_by_email(db, details.email)
        if not attendee:
            attendee = attendee_crud.create_attendee(db, AttendeeCreate(email=details.email, hashed_password=uuid.uuid1().hex[:16]))
            attendee = attendee_crud.update_attendee_by_uuid(db, attendee.user_id, AttendeeUpdate(first_name=details.first_name, last_name=details.last_name))
        session["attendee_id"] = attendee.id
        redis_crud.update_session_in_redis(details.session_id, session)
        logging.info(f"Added attendee {attendee.id} to session {details.session_id}")
        return attendee
    except HTTPException as e:
        logging.exception(str(e))
        raise e
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/checkout/{session_id}")
async def delete_checkout(session_id: str, user = Depends(basic_auth)):
    try:
        value = redis_crud.delete_data_from_redis(session_id)
        if value == 0:
            logging.exception(f"Session {session_id} expired")
            raise HTTPException(status_code=404, detail=f"Session {session_id} expired")
        logging.info(f"Session {session_id} deleted")
        return {"message": f"Session {session_id} deleted"}
    except HTTPException as e:
        logging.exception(str(e))
        raise e
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkout/create-order", response_model=OrderResponse)
async def create_order(create_order_request: CreateOrderRequest, db: Session = Depends(get_db), user = Depends(basic_auth)):
    try:
        conference = conferences_crud.get_conference(db, create_order_request.event_id)
        if conference is None:
            logging.exception(f"Conference {create_order_request.event_id} not found")
            raise HTTPException(status_code=404, detail=f"Conference {create_order_request.event_id} not found")
        session_bytes = redis_crud.get_session_from_redis(create_order_request.session_id)
        if session_bytes is None:
            redis_crud.remove_session_from_list(create_order_request.event_id, create_order_request.session_id)
            logging.exception(f"Session {create_order_request.session_id} not found")
            raise HTTPException(status_code=404, detail=f"Session {create_order_request.session_id} not found")
        session = json.loads(session_bytes)
        reg_setup = registration_setup_crud.get_setup_details(db, conference.id)
        registration_order = registration_order_mapper(reg_setup, session, session["attendee_id"])
        registration_order_items = registration_order_item_mapper(reg_setup.registration_setup_items, session)
        
        total_amount_float = float(registration_order.total_amount)
        razorpay_order = {
            "amount": int(total_amount_float * 100),
            "currency": "INR",
            "receipt": registration_order.uuid
        }
        
        razorpay_order_response = razorpay_crud.create_order(razorpay_client, razorpay_order)
        create_db_order(db, registration_order, registration_order_items, razorpay_order_response["id"])
        response = OrderResponse(message="Order created successfully", event_id=conference.uuid, session_id=create_order_request.session_id, order_id=razorpay_order_response["id"], amount=registration_order.total_amount, currency=razorpay_order["currency"], receipt=razorpay_order["receipt"], payment_status=PaymentStatus.UNPAID)
        logging.info(f"Order {razorpay_order_response['id']} created for conference {conference.uuid}")
        return response
    except HTTPException as e:
        logging.exception(str(e))
        raise e
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/checkout/confirm-order", response_model=list[Ticket])
async def confirm_order(confirm_order_request: ConfirmOrderRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user = Depends(basic_auth)):
    try:
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
            logging.exception(f"Order {confirm_order_request.order_id} not found")
            raise HTTPException(status_code=404, detail=f"Order {confirm_order_request.order_id} not found")
        reg_setup = registration_setup_crud.get_setup_details(db, conference.id)
        
        is_valid = razorpay_crud.verify_payment(order_id=confirm_order_request.order_id, payment_id=confirm_order_request.payment_id, 
        razorpay_signature=confirm_order_request.signature, razorpay_key=razorpay_key_secret)
        if not is_valid:
            logging.exception("Invalid payment")
            raise HTTPException(status_code=400, detail="Invalid payment")
        # razorpay_crud.capture_payment(razorpay_client, confirm_order_request.payment_id, reg_order.total_amount)
        
        payment_timestamp_unix = razorpay_crud.get_payment_timestamp(razorpay_client, confirm_order_request.payment_id)
        payment_timestamp = datetime.fromtimestamp(payment_timestamp_unix)
        order_details = razorpay_crud.get_order_details(razorpay_client=razorpay_client, order_id=confirm_order_request.order_id)
        
        transaction = transaction_crud.transaction_mapper(payment_timestamp=payment_timestamp, amount=reg_order.total_amount, currency=order_details["currency"],event_id=conference.id, order_id=reg_order.id, attendee_id=reg_order.attendee_id, transaction_type_id=t_type.TransactionType.PAYMENT.value, transaction_method_id=t_method.TransactionMethods.RAZOR.value, razorpay_payment_id=confirm_order_request.payment_id,razorpay_signature=confirm_order_request.signature)
                                                        
        transaction_crud.create_transaction(db, transaction)
        
        deduct_tickets_from_available_quantity(db, reg_setup, session)
        reg_order.payment_status = PaymentStatus.PAID.value
        db.commit()
        tickets = add_tickets(db, reg_order, conference.uuid)
        redis_crud.delete_data_from_redis(confirm_order_request.session_id)
        redis_crud.remove_session_from_list(confirm_order_request.event_id, confirm_order_request.session_id)
        
        for ticket in tickets:
            background_tasks.add_task(update_ticket, ticket.ticket_id, db)
            
        logging.info(f"Order {confirm_order_request.order_id} confirmed successfully")
        return tickets
    except HTTPException as e:
        logging.exception(str(e))
        raise e
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=500, detail=str(e))

def update_ticket(ticket_id: str, db: Session):
    ticket = get_registration_ticket_by_ticket_id(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail='Ticket not found')
    order_item = get_registration_order_item_by_id(db, ticket.registration_order_item_id)
    order = get_registration_order_by_id(db, order_item.registration_order_id)
    event = conferences_crud.get_conference_by_id(db, order.event_id)
    tickets = get_tickets_by_attendee_id_and_event_id(db, order.attendee_id, order.event_id)
    template_id = 'tem-cbd6cb4a-fff3-4778-94a4-59b737561cdf'
    template = get_master_template_by_id(db, template_id)
    pdf_ticket = generate_pdf_tickets(db, tickets, template, event, upload=True)
    ticket_ids = []
    for ticket in tickets:
        ticket.ticket_url = pdf_ticket['url']
        update_registration_ticket(db, ticket.ticket_id, ticket)
        logging.info(f"Ticket {ticket.ticket_id} updated with url {pdf_ticket['url']}")
        ticket_ids.append(ticket.ticket_id)
    logging.info(f"Tickets {ticket_ids} updated successfully")
    
    attendee = attendee_crud.get_attendee_by_id(db, order.attendee_id)
    
    send_tickets(receiver_email=attendee.user.email, blob_url=pdf_ticket['url'], subject=f"Tickets for {event.name}")
    logging.info(f"Tickets sent to {attendee.user.email}")