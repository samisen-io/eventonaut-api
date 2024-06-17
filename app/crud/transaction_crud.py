from ..models import Transaction
from ..static_enums import transaction_types as t_type, transaction_methods as t_method
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import uuid

def transaction_mapper(payment_timestamp, amount: float, currency: str, event_id: int, order_id: int, attendee_id: int, transaction_type_id: int, transaction_method_id: int, razorpay_payment_id: str, razorpay_signature: str):
    transaction = Transaction()
    transaction.uuid = f"trn-{uuid.uuid4()}"
    transaction.created_on = datetime.utcnow()
    transaction.transaction_time_stamp = payment_timestamp
    transaction.payment_amount = amount
    transaction.currency = currency
    transaction.event_id = event_id
    transaction.order_id = order_id
    transaction.attendee_id = attendee_id
    transaction.transaction_type_id = transaction_type_id
    transaction.transaction_method_id = transaction_method_id
    transaction.razorpay_payment_id = razorpay_payment_id
    transaction.razorpay_signature = razorpay_signature
    return transaction
    
def create_transaction(db: Session, transaction: Transaction):
    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))