from fastapi import APIRouter, Depends, HTTPException, Security, status
import logging
from sqlalchemy.orm import Session
from app.oauth2 import get_current_active_organization, get_current_active_user
from app.static_enums.organizer import OrganizerEnum
from app.static_enums.role import RoleEnum
from ..schemas import user_schemas as schemas
from ..crud import users_crud as crud
from ..dependencies import get_db
from email_validator import validate_email, EmailNotValidError
from app.schemas.user_schemas import UserAuthentication as User
from .. import basicauth, hashing
from .. import models
from cachetools import TTLCache
import os
from ..otp_generator import send_mail, generate_otp, validate_otp
from app.services.signup_service import signup_organization_admin
from app.schemas import signup_schemas
from ..hashing import verify_hash, get_hash
from ..email_templates.forgot_password import ForgotPasswordEnum
from app.schemas import signup_schemas as s_schemas

default_time_limit = int(os.getenv("OTP_EXPIRE"))
router = APIRouter(tags=["users"], prefix="/user")
cache = TTLCache(maxsize=1024, ttl=default_time_limit)

def validate_user_email(user: schemas.UserCreate):
    try:
        valid = validate_email(user.email)
        user.email = valid.normalized.lower()
    except EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user

async def send_otp(email: str, email_subject: str):
    otp = generate_otp()
    if not send_mail(otp, email_subject, email):
        logging.exception("Email not sent")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not sent")
    return otp

def get_role_ids(user: schemas.UserCreate):
    role_ids = set()
    for role_name in user.list_of_roles:
        try:
            role_id = RoleEnum[role_name.upper()].value
        except KeyError as exc:
            logging.exception("Role not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found") from exc
        role_ids.add(role_id)
    return list(role_ids)

async def check_user_exists(db: Session, user: schemas.UserCreate):
    global cache
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        logging.exception("Email already registered")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    if user.profile_image_url is not None:
        user.profile_image_url = crud.validate_image_url(user.profile_image_url)
    otp = await send_otp(email=user.email, email_subject="Email Verification")
    cache[user.email] = [otp, False, user]
    logging.info("OTP sent to Email")
    return {"msg": "OTP sent successfully"}
    
@router.post("/verify", response_model=schemas.User, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def verify_otp(otp_validation: schemas.OtpVerification, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    global cache
    
    if otp_validation.email not in cache.keys():
        logging.exception("Email not verified")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not verified")
    if len(otp_validation.otp) != 6:
        logging.exception("Invalid OTP")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
    valid_otp = validate_otp(cache[otp_validation.email][0], otp_validation.otp)
    if not valid_otp:
        logging.exception("Invalid OTP")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
    user = cache[otp_validation.email][2]
    del cache[otp_validation.email]
    
    signup_response = signup_organization_admin(db=db, organizer_signup_request = s_schemas.SignupOrganizerAdminRequest(email=user.email, password=user.hashed_password, organization_name=user.company))
    updated_user = update_user(user, current_user_id=signup_response.user_id, db = db)
    updated_user.company = signup_response.organization_name
    return updated_user

def get_role_names(user: schemas.User):
    roles_names = []
    for user_role in user.user_roles:
        if user_role.role_id is None:
            roles_names.append('')
        else:
            role_name = RoleEnum(user_role.role_id).name
            roles_names.append(role_name)
    roles_names = [role for role in roles_names if role != '']
    return roles_names

@router.post("/", include_in_schema=False)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    try:  
        user = validate_user_email(user)
        return await check_user_exists(db, user)
    except Exception as e:
        logging.exception("User not created" + str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not created" + str(e))
    
def get_users_from_db(db: Session, offset: int, limit: int):
    users = crud.get_users(db, offset=offset, limit=limit)
    if users is None or len(users) == 0:
        logging.exception("No user found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
    return users

def assign_role_names_to_users(users):
    for user in users:
        user.list_of_roles = get_role_names(user)
    return users

@router.get("/all_users", response_model=list[schemas.User])
def get_all_users(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = get_users_from_db(db, offset, limit)
    users = assign_role_names_to_users(users)
    logging.info("Users retrieved")
    return users

@router.get("/organization_id", response_model=list[schemas.User], include_in_schema=False)
def get_users_by_organization_id(offset: int = 0, limit: int = 100, db: Session = Depends(get_db), organization: models.Organization = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    try:
        users = crud.get_users_by_organization_id(db, organization.id, offset, limit)
        if users is None or len(users) == 0:
            logging.exception("No user found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user found")
        users = assign_role_names_to_users(users)
        logging.info("Users retrieved")
        return users
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=schemas.User)
def get_user(db: Session = Depends(get_db), current_user:  User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logging.info("User retrieved: " + db_user.uuid)
    db_user.list_of_roles = get_role_names(db_user)
    return db_user

@router.put("/", response_model=schemas.User)
def update_user_(user: schemas.UserBaseUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    if user.profile_image_url is not None:
        user.profile_image_url = crud.validate_image_url(user.profile_image_url)
    db_user = crud.get_db_user(db, user_id=current_user.id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updated_user = crud.update_user(db=db, user=user, db_user=db_user)
    logging.info("User updated: " + updated_user.uuid)
    
    updated_user_response = schemas.User(
        email=updated_user.email,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        timezone=updated_user.timezone,
        status= OrganizerEnum(updated_user.user_status_id).name,
        profile_image_url=updated_user.profile_image_url,
        list_of_roles= get_role_names(updated_user),
        is_active=updated_user.is_active,
        uuid=updated_user.uuid
    )
    return updated_user_response

def get_db_user(db: Session, user_id: int):
    db_user = crud.get_db_user(db, user_id=user_id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user

def validate_passwords(user: schemas.UserPasswordUpdate, db_user: models.User):
    if user.old_password == user.new_password:
        logging.exception("New password cannot be same as old password")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password cannot be same as old password")
    if not hashing.verify_hash(user.old_password, db_user.hashed_password):
        logging.exception("Incorrect old password")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")

@router.put("/password", response_model=schemas.User, include_in_schema=False)
def update_user_password(user: schemas.UserPasswordUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    db_user = get_db_user(db, current_user.id)
    validate_passwords(user, db_user)
    updated_user = crud.update_user_password(db=db, user=user, db_user=db_user)
    logging.info("User password updated: " + updated_user.uuid)
    return updated_user

@router.delete("/")
def delete_user(db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    deleted_user = crud.delete_user(db=db, user=db_user)
    logging.info("User deleted: " + db_user.uuid)
    return deleted_user

def update_user(user: schemas.UserBaseUpdate, current_user_id: str, db: Session = Depends(get_db)):
    if user.profile_image_url is not None:
        user.profile_image_url = crud.validate_image_url(user.profile_image_url)
    db_user = crud.get_user_by_uuid(db, user_uuid=current_user_id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updated_user = crud.update_user(db=db, user=user, db_user=db_user)
    logging.info("User updated: " + updated_user.uuid)
    
    updated_user_response = schemas.User(
        email=updated_user.email,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        timezone=updated_user.timezone,
        status= OrganizerEnum(updated_user.user_status_id).name,
        profile_image_url=updated_user.profile_image_url,
        list_of_roles= get_role_names(updated_user),
        is_active=updated_user.is_active,
        uuid=updated_user.uuid
    )
    return updated_user_response

@router.put("/reset-password", response_model=signup_schemas.SignupOrganizerResponse)
def reset_password(user: schemas.UserPasswordReset, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if verify_hash(plain_text=db_user.uuid, hashed_text=user.uid):
        updated_user = crud.update_user_password(db=db, password=user.password, db_user=db_user)
        organization = updated_user.organization_user[0].organization
        response = signup_schemas.SignupOrganizerResponse(email=user.email, 
                                    uuid=updated_user.uuid,
                                    first_name=updated_user.first_name,
                                    last_name=updated_user.last_name,
                                    timezone=updated_user.timezone,
                                    profile_image_url=updated_user.profile_image_url,
                                    organization_name=organization.name,
                                    status= OrganizerEnum(updated_user.user_status_id).name,
                                    organization_id=organization.uuid,
                                    list_of_roles= get_user_role_ids(updated_user))
        return response
    else:
        logging.exception("Invalid token")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")
    
def get_user_role_ids(user):
    list_of_roles = []
    for user_role in user.user_roles:
        try:
            role_name = RoleEnum(user_role.role_id).name
            list_of_roles.append(role_name)
        except ValueError:
            print(f"Invalid role_id: {user_role.role_id}")
    return list_of_roles
    
@router.put("/forgot-password")
def forgot_password(reset_password: schemas.ForgotPassword, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    db_user = crud.get_user_by_email(db, reset_password.email)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    hashed_uuid = get_hash(db_user.uuid)
    send_mail(unique_id=hashed_uuid, receiver_email=reset_password.email, subject="Reset Password", first_name=db_user.first_name, email_template=ForgotPasswordEnum)
    return {"msg": "Password reset link sent successfully"}