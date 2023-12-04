from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
import logging
from ..dependencies import get_db
from ..crud import users_crud as crud
from email_validator import validate_email, EmailNotValidError
from ..otp_generator import send_mail, generate_otp, validate_otp
from sqlalchemy.orm import Session
from datetime import datetime
from ..crud import users_crud as crud
from dotenv import load_dotenv
import os
import time
from .. import basicauth

load_dotenv()

default_time_limit = int(os.getenv("OTP_EXPIRE"))
router = APIRouter(tags=['OTP'])

class OTPManager:
    def __init__(self):
        self.otp_db = {}

otp_manager = OTPManager()

def get_otp_manager():
    return otp_manager

def delete_entry(email: str,delay: int,task_timestamp: datetime, otp_manager: OTPManager = Depends(get_otp_manager)):
    time.sleep(delay)
    otp_db = otp_manager.otp_db
    entry_timestamp: datetime = otp_db[email][1]
    if email in otp_db.keys() and (entry_timestamp - task_timestamp).total_seconds() == 0:
        del otp_db[email]

@router.post('/otp')
async def send_otp(bgtask:BackgroundTasks, email: str, email_subject: str, otp_manager: OTPManager = Depends(get_otp_manager), db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    global default_time_limit
    otp_db = otp_manager.otp_db
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    user = crud.get_user_by_email(db, email)
    if not user:
        logging.exception("User not found")
        raise HTTPException(status_code=404, detail="User not found")
    otp = generate_otp()
    if not send_mail(otp, email_subject, email):
        logging.exception("Email not sent")
        raise HTTPException(status_code=400, detail="Email not sent")
    sent_time = datetime.now()
    otp_db[email] = [otp, sent_time, False]
    bgtask.add_task(delete_entry, email, default_time_limit, sent_time)
    logging.info("OTP sent to Email")
    return {"msg": "OTP sent successfully"}

@router.post('/otp/verify')
async def verify_otp(email: str, otp: str, otp_manager: OTPManager = Depends(get_otp_manager), basic_auth = Depends(basicauth.basic_auth)):
    otp_db = otp_manager.otp_db
    if email not in otp_db.keys():
        logging.exception("Email not found")
        raise HTTPException(status_code=400, detail="Email not verified")
    if len(otp) != 6:
        logging.exception("Invalid OTP")
        raise HTTPException(status_code=400, detail="Invalid OTP")
    valid_otp = validate_otp(otp_db[email][0], otp, otp_db[email][1], datetime.now())
    otp_db[email][2] = valid_otp
    if valid_otp:
        otp_db[email][0] = 0
    else:
        logging.info("OTP not verified for Email")
        raise HTTPException(status_code=400, detail="Invalid OTP or OTP expired")
    logging.info("OTP verified for Email")
    return {"msg": "OTP verified successfully"}

@router.put('/otp/passwordreset')
async def password_reset(email: str, password: str, otp_manager: OTPManager = Depends(get_otp_manager), db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    otp_db = otp_manager.otp_db
    if email in otp_db.keys() and otp_db[email][2]:
        crud.update_user_password_by_email(db=db, email=email, password=password)
        del otp_db[email]
        logging.info("Password updated for Email")
        return {"msg": "Password updated successfully"}
    else:
        logging.exception("OTP not verified")
        raise HTTPException(status_code=400, detail="OTP not verified")