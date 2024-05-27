import logging
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
from app import basicauth
from ..schemas.user_schemas import UserAuthentication as User
from app.oauth2 import get_current_active_user
from app.schemas import signup_schemas as schemas
from app.dependencies import get_db
from app.services import signup_service
from app.crud import users_crud
from app.static_enums.role import RoleEnum
from ..otp_generator import send_mail
from ..hashing import get_hash
from ..email_templates.welcome_user import WelcomeUserEnum
from email_validator import validate_email, EmailNotValidError

router = APIRouter(tags=["signup_organizer"])

async def send_email(uuid, email, subject, first_name, email_template):
    send_mail(unique_id = uuid, receiver_email = "greengoblin846529@proton.me", subject = subject, first_name = first_name, email_template = email_template)

@router.post("/signup_organization_admin", status_code=201)
async def signup_organization_admin(organizer_signup_request: schemas.SignupOrganizerAdminRequest, db: Session = Depends(get_db), basic_auth = Depends(basicauth.basic_auth)):
    organizer_signup_request.email = validate_user_email(organizer_signup_request.email)
    response = signup_service.signup_organization_admin(db=db, organizer_signup_request = organizer_signup_request)
    hashed_uuid = get_hash(response.uuid)
    await send_email(hashed_uuid, organizer_signup_request.email, "Welcome to the organization", organizer_signup_request.first_name, email_template = WelcomeUserEnum)
    return {"message": "Admin created successfully. Please check your email to activate your account."}

@router.post("/signup_organization_user", response_model=schemas.SignupOrganizerResponse, status_code=201)
async def signup_organization_user(organizer_signup_request: schemas.SignupOrganizerUserRequest, current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name]), db: Session = Depends(get_db)):
    organizer_signup_request.email = validate_user_email(organizer_signup_request.email)
    organization_id = current_user.organization_user[0].organization_id
    response = signup_service.signup_organization_user(db=db, organizer_signup_request = organizer_signup_request, organization_id=organization_id)
    hashed_uuid = get_hash(response.uuid)
    await send_email(hashed_uuid, organizer_signup_request.email, "Welcome to the organization", organizer_signup_request.first_name, email_template = WelcomeUserEnum)
    return response

def get_user_role_ids(user):
    list_of_roles = []
    for user_role in user.user_roles:
        try:
            role_name = RoleEnum(user_role.role_id).name
            list_of_roles.append(role_name)
        except ValueError:
            print(f"Invalid role_id: {user_role.role_id}")
    return list_of_roles

def is_list_of_roles_contains_admin(list_of_roles):
    return RoleEnum.ORGANIZATION_ADMIN.name in list_of_roles

def validate_user_email(email):
    try:
        valid = validate_email(email)
        email = valid.normalized.lower()
    except EmailNotValidError as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return email