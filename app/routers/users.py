from fastapi import APIRouter, Depends, HTTPException, Security, status
import logging
from sqlalchemy.orm import Session
from app.oauth2 import get_current_active_user
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

default_time_limit = int(os.getenv("OTP_EXPIRE"))
router = APIRouter(tags=["users"])
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
    if not send_mail(otp, "Email Verification", email):
        logging.exception("Email not sent")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not sent")
    return otp

@router.post("/users", status_code=status.HTTP_200_OK)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    global cache
    try:
        valid = validate_email(user.email)
        user.email = valid.normalized.lower()
    except EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user

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
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        logging.exception("Email already registered")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    crud.validate_image_url(user.profile_image_url)
    otp = await send_otp(email=user.email, email_subject="Email Verification")
    cache[user.email] = [otp, False, user]
    logging.info("OTP sent to Email")
    return {"msg": "OTP sent successfully"}
    
@router.post("/users/verify", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def verify_otp(email: str, otp: str, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    global cache
    if email not in cache.keys():
        logging.exception("Email not verified")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not verified")
    if len(otp) != 6:
        logging.exception("Invalid OTP")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
    valid_otp = validate_otp(cache[email][0], otp)
    if not valid_otp:
        logging.exception("Invalid OTP")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
    user = cache[email][2]

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

@router.post("/users", response_model=schemas.User, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    user = validate_user_email(user)
    role_ids = get_role_ids(user)
    await check_user_exists(db, user)
    try:
        user = crud.create_user(db=db, user=user, role_ids=role_ids)
        user.list_of_roles = get_role_names(user)
        logging.info("User created: " + user.uuid)
        del cache[user.email]
        return user
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
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

@router.get("/users/all_users", response_model=list[schemas.User])
def get_all_users(offset: int = 0, limit: int = 100, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    users = get_users_from_db(db, offset, limit)
    users = assign_role_names_to_users(users)
    logging.info("Users retrieved")
    return users

@router.get("/users", response_model=schemas.User)
def get_user(db: Session = Depends(get_db), current_user:  User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    logging.info("User retrieved: " + db_user.uuid)
    db_user.list_of_roles = get_role_names(db_user)
    return db_user

@router.put("/users", response_model=schemas.User)
def update_user(user: schemas.UserBaseUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
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
    if not hashing.verify_password(user.old_password, db_user.hashed_password):
        logging.exception("Incorrect old password")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect old password")

@router.put("/users/password", response_model=schemas.User)
def update_user_password(user: schemas.UserPasswordUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    db_user = get_db_user(db, current_user.id)
    validate_passwords(user, db_user)
    updated_user = crud.update_user_password(db=db, user=user, db_user=db_user)
    logging.info("User password updated: " + updated_user.uuid)
    return updated_user

@router.delete("/users")
def delete_user(db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"])):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        logging.exception("User not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    deleted_user = crud.delete_user(db=db, user=db_user)
    logging.info("User deleted: " + db_user.uuid)
    return deleted_user