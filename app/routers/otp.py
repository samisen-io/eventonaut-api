from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
import logging
from ..dependencies import get_db
from ..crud import users_crud as crud
from email_validator import validate_email, EmailNotValidError
from ..otp_generator import send_mail, generate_otp, validate_otp
from sqlalchemy.orm import Session
from datetime import datetime
from ..crud import users_crud as crud
from cachetools import TTLCache
from dotenv import load_dotenv
import os
import time
from .. import basicauth

load_dotenv()

default_time_limit = int(os.getenv("OTP_EXPIRE"))
router = APIRouter(tags=['OTP'])
cache = TTLCache(maxsize=1024, ttl=default_time_limit)

@router.post('/otp')
async def send_otp(bgtask:BackgroundTasks, email: str, email_subject: str, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    global cache
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    user = crud.get_user_by_email(db, email)
    if not user:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    otp = generate_otp()
    if not send_mail(otp, email_subject, email):
        logging.exception("Email not sent")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not sent")
    cache[email] = [otp, False]
    logging.info("OTP sent to Email")
    return {"msg": "OTP sent successfully"}

@router.post('/otp/verify')
async def verify_otp(email: str, otp: str, basic_auth = Depends(basicauth.basic_auth)):
    global cache
    if email not in cache.keys():
        logging.exception("Email not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not verified")
    if len(otp) != 6:
        logging.exception("Invalid OTP")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
    valid_otp = validate_otp(cache[email][0], otp)
    cache[email][1] = valid_otp
    if valid_otp:
        cache[email][0] = 0
    else:
        logging.info("OTP not verified for Email")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP or OTP expired")
    logging.info("OTP verified for Email")
    return {"msg": "OTP verified successfully"}

@router.put('/otp/passwordreset')
async def password_reset(email: str, password: str, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    global cache
    if email in cache.keys() and cache[email][1]:
        crud.update_user_password_by_email(db=db, email=email, password=password)
        del cache[email]
        logging.info("Password updated for Email")
        return {"msg": "Password updated successfully"}
    else:
        logging.exception("OTP not verified")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP not verified")
    
@router.put('/otp/password-reset-attendee')
async def password_reset_attendee(otp:str, email: str, password: str, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    await verify_otp(email=email,otp=otp)
    return await password_reset(email=email,password=password,db=db)