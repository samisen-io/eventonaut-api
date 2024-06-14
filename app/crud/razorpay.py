import hashlib
import hmac
from fastapi import HTTPException, status

def create_order(razorpay_client, data):
    try:
        response = razorpay_client.order.create(data=data)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
def verify_payment(order_id: str, payment_id: str, razorpay_signature: str, razorpay_key: str):
    try:
        params_dict = {
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": razorpay_signature
        }
        generated_signature = hmac.new(razorpay_key.encode(), f"{params_dict['razorpay_order_id']}|{params_dict['razorpay_payment_id']}".encode(), hashlib.sha256).hexdigest()
        if generated_signature == params_dict["razorpay_signature"]:
            return True
        else:
            return False
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
def capture_payment(razorpay_client, payment_id: str, amount: int):
    try:
        response = razorpay_client.payment.capture(payment_id, amount)
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))