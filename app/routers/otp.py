from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
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

load_dotenv()

default_time_limit = int(os.getenv("OTP_EXPIRE"))
router = APIRouter(tags=['OTP'])
otp_db = dict()

def delete_entry(email: str,delay: int,task_timestamp: datetime):
    time.sleep(delay)
    global otp_db
    entry_timestamp: datetime = otp_db[email][1]
    if email in otp_db.keys() and (entry_timestamp - task_timestamp).total_seconds() == 0:
        del otp_db[email]

@router.post('/otp')
async def send_otp(bgtask:BackgroundTasks,email: str, email_subject: str , db: Session = Depends(get_db)):
    global otp_db, default_time_limit
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    otp = generate_otp()
    if not send_mail(otp, email_subject, email):
        raise HTTPException(status_code=400, detail="Email not sent")
    sent_time = datetime.now()
    otp_db[email] = [otp, sent_time, False]
    bgtask.add_task(delete_entry, email, default_time_limit, sent_time)
    return {"msg": "OTP sent successfully"}

@router.post('/otp/verify')
async def verify_otp(email: str, otp: str):
    global otp_db
    if email not in otp_db.keys():
        raise HTTPException(status_code=400, detail="Email not verified")
    if len(otp) != 6:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    valid_otp = validate_otp(otp_db[email][0], otp, otp_db[email][1], datetime.now())
    if valid_otp:
        otp_db[email][2] = valid_otp
        otp_db[email][0] = 0
    if not valid_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP or OTP expired")
    return {"msg": "OTP verified successfully"}

@router.put('/otp/passwordreset')
async def password_reset(email: str, password: str, db: Session = Depends(get_db)):
    global otp_db
    if email in otp_db.keys() and otp_db[email][2]:
        crud.update_user_password_by_email(db=db, email=email, password=password)
        del otp_db[email]
        return {"msg": "Password updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="OTP not verified")