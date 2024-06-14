from sqlalchemy.orm import Session
from app.crud import users_crud, organization_crud, organization_user_crud
from app.schemas import signup_schemas as schemas, user_schemas, organization_schemas, organization_user_schemas
from app.static_enums.role import RoleEnum
from app.static_enums.organizer import OrganizerEnum
from app.models import User
import uuid

def create_organization(db: Session, name: str):
    create_organizer_request = organization_schemas.OrganizationCreate(name=name)
    return organization_crud.create_organization(db=db, organization=create_organizer_request)

def create_user(db: Session, user: user_schemas.UserCreate, user_role: RoleEnum):
    return users_crud.create_user_with_roles(db=db, user=user, role_ids=[user_role.value])

def create_organization_user(db: Session, organization_id: str, user_id: str):
    organization_user = organization_user_schemas.Organization_UserCreate(organization_id=organization_id, user_id=user_id)
    return organization_user_crud.create_organization_user(db=db, organization_user=organization_user)

def signup_organization_admin(db: Session, organizer_signup_request: schemas.SignupOrganizerAdminRequest):
    admin_password = uuid.uuid1().hex[:16]
    organization = create_organization(db, organizer_signup_request.organization_name)
    user = create_user(db, user_schemas.UserCreate(email=organizer_signup_request.email, hashed_password=admin_password, first_name=organizer_signup_request.first_name, last_name=organizer_signup_request.last_name, timezone=organizer_signup_request.timezone, status=OrganizerEnum.INACTIVE.name), RoleEnum.ORGANIZATION_ADMIN)
    org_user = create_organization_user(db, organization.uuid, user.uuid)
    
    signup_organizer_response = schemas.SignupResponseBase(email=user.email, 
                                    uuid=user.uuid,
                                    db_id=user.id,
                                    first_name=user.first_name,
                                    last_name=user.last_name,
                                    timezone=user.timezone,
                                    profile_image_url=user.profile_image_url,
                                    organization_name=organization.name,
                                    status= OrganizerEnum(user.user_status_id).name,
                                    organization_id=organization.uuid, 
                                    user_id=user.uuid, 
                                    list_of_roles= get_user_role_ids(user),
                                    is_verified=user.is_verified
                                    )
    signup_organizer_response = schemas.SignupOrganizerResponse(user=signup_organizer_response.model_dump(),uuid=org_user.uuid)
        
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

def signup_organization_user(db: Session, organizer_signup_request: schemas.SignupOrganizerUserRequest, organization_id: int):
    user_password = uuid.uuid1().hex[:16]
    organization = organization_crud.get_organization_by_id(db, organization_id)
    user = create_user(db, user_schemas.UserCreate(email=organizer_signup_request.email, hashed_password=user_password, first_name=organizer_signup_request.first_name, last_name=organizer_signup_request.last_name, timezone=organizer_signup_request.timezone, status=OrganizerEnum.INACTIVE.name), RoleEnum.__members__.get(organizer_signup_request.user_role))
    org_user = create_organization_user(db, organization.uuid, user.uuid)
    
    signup_organizer_response = schemas.SignupResponseBase(email=user.email,
                                    uuid=user.uuid,
                                    db_id=user.id,
                                    first_name=user.first_name,
                                    last_name=user.last_name,
                                    timezone=user.timezone,
                                    profile_image_url=user.profile_image_url,
                                    organization_name=organization.name, 
                                    status= OrganizerEnum(user.user_status_id).name,
                                    organization_id=organization.uuid, 
                                    user_id=user.uuid, 
                                    list_of_roles= get_user_role_ids(user),
                                    is_verified=user.is_verified
                                    )
    
    signup_organizer_response = schemas.SignupOrganizerResponse(user=signup_organizer_response.model_dump(),uuid=org_user.uuid)
    
    return signup_organizer_response

def get_organization_uuid(admin_organizations: organization_user_schemas.UserOrganizationsResponse, organization_name: str) -> str:
    for organization in admin_organizations.organizations:
        if organization.name == organization_name:
            return organization.uuid
    return None