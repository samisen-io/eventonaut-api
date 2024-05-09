from fastapi import APIRouter, Depends, HTTPException, status
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
from ..schemas.otp_schemas import SendOtp, VerifyOtp, PasswordReset, PasswordResetForAttendee

load_dotenv()

default_time_limit = int(os.getenv("OTP_EXPIRE"))
router = APIRouter(tags=['OTP'])
cache = TTLCache(maxsize=1024, ttl=default_time_limit)

@router.post('/otp')
async def send_otp(send_otp: SendOtp, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    global cache
    try:
        valid = validate_email(send_otp.email)
        email = valid.email
    except EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    user = crud.get_user_by_email(db, email)
    if not user:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    roles = [user_role.role for user_role in user.user_roles]
    if send_otp.role not in [role.name for role in roles]:
        logging.exception("Email not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not found")
    otp = generate_otp()
    if not send_mail(otp, send_otp.email_subject, email):
        logging.exception("Email not sent")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not sent")
    cache[email] = [otp, False, send_otp.role]
    logging.info("OTP sent to Email")
    return {"msg": "OTP sent successfully"}

@router.post('/otp/verify')
async def verify_otp(verify_otp: VerifyOtp, basic_auth = Depends(basicauth.basic_auth)):
    global cache
    if verify_otp.email not in cache.keys():
        logging.exception("Email not verified")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not verified")
    elif cache[verify_otp.email][2] != verify_otp.role:
        logging.exception("Email not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not found")
    if len(verify_otp.otp) != 6:
        logging.exception("Invalid OTP")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
    valid_otp = validate_otp(cache[verify_otp.email][0], verify_otp.otp)
    cache[verify_otp.email][1] = valid_otp
    if valid_otp:
        cache[verify_otp.email][0] = 0
    else:
        logging.info("OTP not verified for Email")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP or OTP expired")
    logging.info("OTP verified for Email")
    return {"msg": "OTP verified successfully"}

@router.put('/otp/passwordreset')
async def password_reset(password_reset: PasswordReset, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    global cache
    if password_reset.email not in cache.keys() or cache[password_reset.email][2] != password_reset.role:
        logging.exception("Email not found")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not found")
    elif password_reset.email in cache.keys() and cache[password_reset.email][1]:
        crud.update_user_password_by_email(db=db, email=password_reset.email, password=password_reset.password)
        del cache[password_reset.email]
        logging.info("Password updated for Email")
        return {"msg": "Password updated successfully"}
    else:
        logging.exception("OTP not verified")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP not verified")
    
@router.put('/otp/password-reset-attendee')
async def password_reset_attendee(password_reset_dict: PasswordResetForAttendee, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    verify_otp_dict = VerifyOtp(email=password_reset_dict.email,otp=password_reset_dict.otp,role=password_reset_dict.role)
    reset_password = PasswordReset(email=password_reset_dict.email,password=password_reset_dict.password,role=password_reset_dict.role)
    await verify_otp(verify_otp=verify_otp_dict)
    return await password_reset(password_reset=reset_password, db=db, basic_auth=basic_auth)