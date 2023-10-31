from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_db
from ..crud import users_crud as crud
from email_validator import validate_email, EmailNotValidError
from ..otp_generator import send_mail, otp_generator
from sqlalchemy.orm import Session
from datetime import datetime

router = APIRouter(tags=['OTP'])
otp_gen: otp_generator = otp_generator()

@router.post('/otp')
async def send_otp(email: str, email_subject: str , db: Session = Depends(get_db)):
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    send_mail(otp_gen, email_subject, email)
    return {"msg": "OTP sent successfully"}

@router.post('/otp/verify')
async def verify_otp(email: str, otp: int, db: Session = Depends(get_db)):
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    otp_status = otp_gen.validate_otp(otp, datetime.now())
    if not otp_status:
        raise HTTPException(status_code=400, detail="Invalid OTP or OTP expired")
    return {"msg": "OTP verified successfully"}