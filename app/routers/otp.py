from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_db
from ..crud import users_crud as crud
from email_validator import validate_email, EmailNotValidError
from ..otp_generator import send_mail, otp_generator
from sqlalchemy.orm import Session
from datetime import datetime
from ..crud import users_crud as crud

router = APIRouter(tags=['OTP'])
otp_gen: otp_generator = otp_generator()
valid_otp: bool = False
valid_email: str = ""

@router.post('/otp')
async def send_otp(email: str, email_subject: str , db: Session = Depends(get_db)):
    global valid_email
    try:
        valid = validate_email(email)
        email = valid.email
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))
    user = crud.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    send_mail(otp_gen, email_subject, email)
    valid_email = email
    return {"msg": "OTP sent successfully"}

@router.post('/otp/verify')
async def verify_otp(email: str, otp: str, db: Session = Depends(get_db)):
    global valid_otp, valid_email
    if email != valid_email:
        raise HTTPException(status_code=400, detail="Email not verified")
    if len(otp) != 6:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    valid_otp = otp_gen.validate_otp(otp, datetime.now())
    if not valid_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP or OTP expired")
    return {"msg": "OTP verified successfully"}

@router.put('/otp/passwordreset')
async def password_reset(email: str, password: str, db: Session = Depends(get_db)):
    global valid_otp, valid_email
    if valid_otp and email == valid_email:
        user = crud.get_user_by_email(db, email)
        crud.update_user_password_by_id(db, user_id=user.id, password=password)
        valid_otp = False
        return {"msg": "Password updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="OTP not verified")