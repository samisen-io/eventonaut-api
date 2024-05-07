import logging
import os
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from urllib.parse import urlparse
from sqlalchemy.orm import Session, joinedload
from app.static_enums.role import RoleEnum
from .. import models, hashing
from ..schemas import user_schemas as schemas
from datetime import datetime
import uuid
from ..static_enums import organizer
from ..routers import upload_image
from ..crud import user_role_crud
from ..static_enums.blob_container_enums import BlobContainer
from sqlalchemy import text
from app.sql_queries.users_query import query_user_by_email_and_archived_status

def create_db_user(db: Session, user: schemas.UserCreate):
    user_dict = user.model_dump()
    user_status = user_dict.pop("status")
    user_profile_image_url = user_dict.pop("profile_image_url")
    user_dict.pop("list_of_roles")
    db_user = models.User(**user_dict)
    db_user.user_status_id = organizer.OrganizerEnum[user_status.upper()].value
    db_user.hashed_password = hashing.get_password_hash(db_user.hashed_password)
    db_user.created_on = db_user.updated_on = datetime.utcnow()
    db_user.uuid = "usr-"+str(uuid.uuid4())
    db_user.role = "organizer"
    db_user.profile_image_url = upload_image.get_actual_url(image_url=user_profile_image_url, new_blob_container=BlobContainer.PROFILE_IMAGES.value, new_blob_name=f"profile-{db_user.uuid}") if user_profile_image_url is not None else None
    return db_user

def validate_image_url(image_url: str):
    parsed_url = urlparse(image_url)
    path = parsed_url.path
    filename_with_ext = os.path.basename(path)
    _, extension = os.path.splitext(filename_with_ext)

    if extension not in ['.jpg', '.jpeg', '.png']:
        logging.exception("Invalid image file format")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file format")
    
    if not upload_image.check_for_blob_in_container(blob_url=image_url, container_name=BlobContainer.TEMPORARY_IMAGES.value):
        logging.exception("Invalid image URL")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image URL")

def create_user(db: Session, user: schemas.UserCreate):
    user_dict = user.model_dump()
    user_status = user_dict.pop("status")
    user_profile_image_url = user_dict.pop("profile_image_url")
    user_dict.pop("list_of_roles")
    db_user = models.User(**user_dict)
    db_user.user_status_id = organizer.OrganizerEnum[user_status.upper()].value
    db_user.hashed_password = hashing.get_password_hash(db_user.hashed_password)
    db_user.created_on = db_user.updated_on = datetime.utcnow()
    db_user.uuid = "usr-"+str(uuid.uuid4())
    db_user.role = "organizer"
    db_user.is_verified = True

    db_user.profile_image_url = upload_image.get_actual_url(image_url=user_profile_image_url, new_blob_container=BlobContainer.PROFILE_IMAGES.value, new_blob_name=f"profile-{db_user.uuid}") if user_profile_image_url is not None else None
    return db_user

def add_user_to_db(db: Session, db_user: models.User):
    db.add(db_user)
    try:
        db.commit()
    except Exception as e:
        if 'unique constraint "ix_users_email"' in str(e):
            raise HTTPException(status_code=400, detail="Email already in use")
        if db_user.profile_image_url is not None:
            upload_image.delete_blob_by_url(db_user.profile_image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=jsonable_encoder(e))
    db.refresh(db_user)

def assign_roles_to_user(db: Session, db_user: models.User, role_ids: list[int]):
    for role_id in role_ids:
        user_role_crud.create_user_role(db, user_id=db_user.id, role_id=role_id)

def create_user_with_roles(db: Session, user: schemas.UserCreate, role_ids: list[int]):
    db_user = create_db_user(db, user)
    add_user_to_db(db, db_user)
    assign_roles_to_user(db, db_user, role_ids)
    return db_user

def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id, models.User.is_archived == False).first()
    return user

def get_users_by_organization_id(db: Session, organization_id: int, offset: int, limit: int):
    # users = db.query(models.User).options(joinedload(models.User.organization_user)).filter(models.Organization_User.organization_id == organization_id, models.User.is_archived == False).offset(offset).limit(limit).all()
    users = (
    db.query(models.User)
    .join(models.Organization_User, models.User.id == models.Organization_User.user_id)
    .join(models.User_Role, models.User.id == models.User_Role.user_id)
    .filter(models.Organization_User.organization_id == organization_id, models.User.is_archived == False)
    .offset(offset)
    .limit(limit)
    .all()
    )
    
    return users

def get_user_by_uuid(db: Session, user_uuid: str):
    try:
        user = db.query(models.User).filter(models.User.uuid == user_uuid, models.User.is_archived == False).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def get_db_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id, models.User.is_archived == False).first()

def get_user_by_email(db: Session, email: str):
    user = db.query(models.User).options(joinedload(models.User.organization_user), joinedload(models.User.user_roles).joinedload(models.User_Role.role)).filter(models.User.email.ilike(email), models.User.is_archived == False).first()
    return user

def get_role_by_user_id(db: Session, user_id: int):
    return db.query(models.Role).join(models.User_Role, models.Role.id == models.User_Role.role_id).filter(models.User_Role.user_id == user_id).all()

def get_active_user_by_email(db: Session, email: str):
    query = text(query_user_by_email_and_archived_status)
    result = db.execute(query, {'email': email}).fetchall()
    if result is None:
        return None
    user = map_to_user(result)
    return user

def get_user_by_email_and_password(db: Session, email: str, password: str):
    try:
        user = db.query(models.User).options(joinedload(models.User.user_roles)).filter(models.User.email.ilike(email), models.User.is_archived == False).first()
        if user is None:
            return False
        if hashing.verify_password(password, user.hashed_password):
            return user
        return False
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def map_to_user(results):
    user = schemas.UserAuthorization(
        id=results[0].id,
        uuid=results[0].uuid,
        email=results[0].email,
        first_name=results[0].first_name,
        last_name=results[0].last_name,
        hashed_password=results[0].hashed_password,
        is_active=results[0].is_active,
        is_verified=results[0].is_verified,
        is_archived=results[0].is_archived,
        user_status_id=results[0].user_status_id,
        role=[result.role for result in results]
    )
    return user
    
def get_users(db: Session, offset: int = 0, limit: int = 100):
    users = db.query(models.User).filter(models.User.role == 'organizer').order_by(models.User.updated_on.desc()).offset(offset).limit(limit).all()
    return users

def update_user_status(user: schemas.UserBaseUpdate, db_user: models.User):
    user_status = user.status
    if user_status is not None:
        db_user.user_status_id = organizer.OrganizerEnum[user_status.upper()].value

def update_user_fields(user: schemas.UserBaseUpdate, db_user: models.User):
    user_dict = user.model_dump()
    user_dict.pop("status")
    user_dict.pop("profile_image_url")
    user_dict.pop("hashed_password")
    non_nullable_fields = ['first_name','last_name','business_type']
    for key, value in user_dict.items():
        if key in non_nullable_fields:
            if value is not None:
                setattr(db_user, key, value)
        else:
            setattr(db_user, key, value)

def update_user_image(user: schemas.UserBaseUpdate, db_user: models.User):
    user_profile_image_url = user.profile_image_url
    if user_profile_image_url is not None and upload_image.get_container_name_from_url(user_profile_image_url) != BlobContainer.PROFILE_IMAGES.value:
        db_user.profile_image_url = upload_image.get_actual_url(image_url=user_profile_image_url, new_blob_container=BlobContainer.PROFILE_IMAGES.value, new_blob_name=f"profile-{db_user.uuid}")
    elif user_profile_image_url is None and db_user.profile_image_url is not None:
        upload_image.delete_blob_by_url(db_user.profile_image_url)
        db_user.profile_image_url = None
    else:
        db_user.profile_image_url = user_profile_image_url

def get_role_names_from_user_roles(user_roles):
    return [RoleEnum(user_role.role_id).name for user_role in user_roles]

def get_roles_not_in_user(db_user, user):
    db_user_role_names = get_role_names_from_user_roles(db_user.user_roles)
    user_role_names = user.list_of_roles
    roles_not_in_user = [role for role in db_user_role_names if role not in user_role_names]
    return roles_not_in_user

def get_roles_not_in_db_user(db_user, user):
    try:
        db_user_role_names = get_role_names_from_user_roles(db_user.user_roles)
        user_role_names = user.list_of_roles
        roles_not_in_db_user = [role for role in user_role_names if role not in db_user_role_names]
        return roles_not_in_db_user
    except Exception as e:
        logging.exception(str(e))
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

def delete_roles_not_in_user(db: Session, db_user: models.User, roles_not_in_user: list):
    for role in roles_not_in_user:
        role_id = RoleEnum[role.upper()].value
        user_role_crud.delete_user_role_by_user_and_role(db, user_id=db_user.id, role_id=role_id)

def create_roles_not_in_db_user(db: Session, db_user: models.User, roles_not_in_db_user: list):
    for role in roles_not_in_db_user:
        role_id = RoleEnum[role.upper()].value
        user_role_crud.create_user_role(db, user_id=db_user.id, role_id=role_id)

def update_user_roles(db: Session, user: schemas.UserBaseUpdate, db_user: models.User):
    if user.list_of_roles is not None:
        is_valid_roles(user.list_of_roles)
        
        roles_not_in_user = get_roles_not_in_user(db_user, user)
        if roles_not_in_user:
            delete_roles_not_in_user(db, db_user, roles_not_in_user)
                
        roles_not_in_db_user = get_roles_not_in_db_user(db_user, user)
        if roles_not_in_db_user:
            create_roles_not_in_db_user(db, db_user, roles_not_in_db_user) 

def is_valid_roles(list_of_roles):
    if not all(role in RoleEnum.__members__ for role in list_of_roles):
        raise HTTPException(status_code=400, detail="Invalid role")   
                
def update_user(db: Session, user: schemas.UserBaseUpdate, db_user: models.User):
    update_user_status(user, db_user)
    update_user_fields(user, db_user)
    update_user_image(user, db_user)
    update_user_roles(db, user, db_user)
    db_user.updated_on = datetime.utcnow()
    try:
        db.commit()
    except Exception as e:
        if user.profile_image_url is not None:
            upload_image.delete_blob_by_url(db_user.profile_image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_user)
    return db_user

def update_user_password(db: Session, user: schemas.UserPasswordUpdate, db_user: models.User):
    db_user.hashed_password = hashing.get_password_hash(user.new_password)
    db_user.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_password_by_email(db: Session, email: str, password: str):
    db_user = db.query(models.User).filter(models.User.email.ilike(email)).first()
    db_user.hashed_password = hashing.get_password_hash(password)
    db_user.updated_on = datetime.utcnow()
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user: models.User):
    db_session = db.query(models.Session).filter(models.Session.organization_id == user.id).all()
    for session in db_session:
        session.is_archived = True
        
    conference = db.query(models.Conference).filter(models.Conference.organization_id == user.id).all()
    for c in conference:
        c.is_archived = True

    user.is_archived = True
    db.commit()
    return True