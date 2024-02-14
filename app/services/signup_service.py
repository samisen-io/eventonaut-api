from sqlalchemy.orm import Session
from app import hashing
from app.crud import users_crud, organization_crud, organization_user_crud, user_role_crud
from app.schemas import signup_schemas as schemas, user_schemas, organization_schemas, organization_user_schemas
from app.static_enums.role import RoleEnum
from app.static_enums.organizer import OrganizerEnum

def create_organization(db: Session, name: str):
    create_organizer_request = organization_schemas.OrganizationCreate(name=name)
    return organization_crud.create_organization(db=db, organization=create_organizer_request)

def create_user(db: Session, email: str, password: str):
    create_user_request = user_schemas.UserCreate(email=email, hashed_password=password, status="active")
    return users_crud.create_user(db=db, user=create_user_request, role_ids=[RoleEnum.ORGANIZATION_ADMIN.value])

def create_organization_user(db: Session, organization_id: str, user_id: str):
    organization_user = organization_user_schemas.Organization_UserCreate(organization_id=organization_id, user_id=user_id)
    return organization_user_crud.create_organization_user(db=db, organization_user=organization_user)

def signup_organizer(db: Session, organizer_signup_request: schemas.SignupOrganizerRequest):
    organization = create_organization(db, organizer_signup_request.organization_name)
    user = create_user(db, organizer_signup_request.email, organizer_signup_request.password)
    create_organization_user(db, organization.uuid, user.uuid)
    
    signup_organizer_response = schemas.SignupOrganizerResponse(email=user.email, 
                                    organization_name=organization.name, 
                                    status= OrganizerEnum(user.user_status_id).name,
                                    organization_id=organization.uuid, 
                                    user_id=user.uuid, 
                                    list_of_roles= get_user_role_ids(user))
    
    
    return signup_organizer_response


def get_user_role_ids(user):
    list_of_roles = []
    for user_role in user.user_roles:
        try:
            role_name = RoleEnum(user_role.role_id).name
            list_of_roles.append(role_name)
        except ValueError:
            print(f"Invalid role_id: {user_role.role_id}")
    return list_of_roles