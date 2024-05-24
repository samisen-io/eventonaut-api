import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud import organization_crud, users_crud
from app.static_enums import organizer
from app.static_enums.organizer import OrganizerEnum
from app.static_enums.role import RoleEnum
from .. import models
from ..schemas import organization_user_schemas as schemas
from ..schemas. user_schemas import UserBaseUpdate
from datetime import datetime
from ..crud.users_crud import delete_user, get_db_user, update_user

def get_organization_user(db: Session, organization_user_id: str, organization_id: int):
    return db.query(models.Organization_User).filter(models.Organization_User.uuid == organization_user_id, models.Organization_User.organization_id == organization_id).first()

def get_organization_user_by_organization_id(db: Session, organization_user_uuid: str):
    return db.query(models.Organization_User).filter(models.Organization_User.uuid == organization_user_uuid).first()

def get_users_by_organization_uuid(db: Session, organization_id: int):
    organization = db.query(models.Organization).filter(models.Organization.id == organization_id).first()
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization with the specified ID not found")
    users = []
    for organization_user in organization.organization_user:
        user = db.query(models.User).filter(models.User.id == organization_user.user_id).first()
        users.append(schemas.OrganizationUserBase(uuid=organization_user.uuid, user=schemas.User(**user.__dict__, list_of_roles=get_user_role_ids(user), status=OrganizerEnum(user.user_status_id).name)))
    return schemas.OrganizationUsersResponse(organization_uuid=organization.uuid, organization_name=organization.name, users=users)

def get_user_role_ids(user):
    list_of_roles = []
    for user_role in user.user_roles:
        try:
            role_name = RoleEnum(user_role.role_id).name
            list_of_roles.append(role_name)
        except ValueError:
            print(f"Invalid role_id: {user_role.role_id}")
    return list_of_roles

def get_organizations_by_user_uuid(db: Session, user_uuid: str):
    user = db.query(models.User).filter(models.User.uuid == user_uuid).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with the specified ID not found")

    organizations = [schemas.OrganizationBase(uuid=organization_user.organization.uuid, name=organization_user.organization.name) 
                     for organization_user in user.organization_user]
    return schemas.UserOrganizationsResponse(user_id=user_uuid, organizations=organizations)

def get_organization_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Organization_User).offset(skip).limit(limit).all()

def get_organization_user_by_organization_id_and_user_id(db: Session, organization_id: int, user_id: int):
    return db.query(models.Organization_User).filter((models.Organization_User.organization_id == organization_id) & (models.Organization_User.user_id == user_id)).first()

def create_organization_user(db: Session, organization_user: schemas.Organization_UserCreate):
    organization = organization_crud.get_organization_by_uuid(db, organization_user.organization_id)
    user = users_crud.get_user_by_uuid(db, organization_user.user_id)
    
    organization_user_exist = get_organization_user_by_organization_id_and_user_id(db, organization.id, user.id)
    
    if organization_user_exist is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization_user already exists")
    
    db_organization_user = models.Organization_User(**organization_user.model_dump())
    db_organization_user.created_on = db_organization_user.updated_on = datetime.utcnow()
    db_organization_user.uuid = "ous-" + str(uuid.uuid4())
    db_organization_user.organization_id = organization.id
    db_organization_user.user_id = user.id
    db.add(db_organization_user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    db.refresh(db_organization_user)
    return db_organization_user

def update_organization_user(db: Session, organization_user: schemas.Organization_UserUpdate, db_organization_user: models.Organization_User):
    db_user = users_crud.get_db_user(db, db_organization_user.user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    update_user_req = UserBaseUpdate(**organization_user.model_dump())
    updated_user = update_user(db, update_user_req, db_user)
    response = schemas.Organization_UserUpdateResponse(first_name=updated_user.first_name, last_name=updated_user.last_name, uuid=updated_user.uuid, status=organizer.OrganizerEnum(updated_user.user_status_id).name, timezone=updated_user.timezone, profile_image_url=updated_user.profile_image_url,id=db_organization_user.uuid, list_of_roles=get_user_role_ids(updated_user))
    return response

def delete_organization_user(db: Session, db_organization_user: models.Organization_User):
    db_user = get_db_user(db, db_organization_user.user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_user = delete_user(db, db_user)
    db.delete(db_organization_user)
    db.commit()
    return True

def get_user_role_ids(user):
    list_of_roles = []
    for user_role in user.user_roles:
        try:
            role_name = RoleEnum(user_role.role_id).name
            list_of_roles.append(role_name)
        except ValueError:
            print(f"Invalid role_id: {user_role.role_id}")
    return list_of_roles