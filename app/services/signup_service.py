from sqlalchemy.orm import Session
from app import hashing
from app.crud import users_crud, organization_crud, organization_user_crud, user_role_crud
from app.schemas import signup_schemas as schemas, user_schemas, organization_schemas, organization_user_schemas
from app.static_enums.role import RoleEnum

def create_organization(db: Session, name: str):
    create_organizer_request = organization_schemas.OrganizationCreate(name=name)
    return organization_crud.create_organization(db=db, organization=create_organizer_request)

def create_user(db: Session, email: str, password: str):
    create_user_request = user_schemas.UserCreate(email=email, hashed_password=password, status="active")
    return users_crud.create_user(db=db, user=create_user_request, role_ids=[RoleEnum.ORGANIZATION_ADMIN.value])

def create_organization_user(db: Session, organization_id: str, user_id: str):
    organization_user = organization_user_schemas.Organization_UserCreate(organization_id=organization_id, user_id=user_id)
    return organization_user_crud.create_organization_user(db=db, organization_user=organization_user)

def signup_organizer(db: Session, organizer_signup_request: schemas.SignupOrganizer):
    organization = create_organization(db, organizer_signup_request.organization_name)
    user = create_user(db, organizer_signup_request.email, organizer_signup_request.password)
    create_organization_user(db, organization.uuid, user.uuid)
    return organizer_signup_request