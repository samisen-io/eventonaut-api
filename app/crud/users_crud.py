import logging
import os
from urllib.parse import urlparse
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from .. import models, hashing
from ..schemas import user_schemas as schemas
from datetime import datetime
import uuid
from ..static_enums import organizer
from ..routers import upload_image
from ..static_enums.blob_container_enums import BlobContainer

def create_user(db: Session, user: schemas.UserCreate):
    user_dict = user.model_dump()
    user_status = user_dict.pop("status")
    user_profile_image_url = user_dict.pop("profile_image_url")
    db_user = models.User(**user_dict)
    db_user.user_status_id = organizer.OrganizerEnum[user_status.upper()].value
    db_user.hashed_password = hashing.get_password_hash(db_user.hashed_password)
    db_user.created_on = db_user.updated_on = datetime.utcnow()
    db_user.uuid = "usr-"+str(uuid.uuid4())
    db_user.role = "organizer"

    db_user.profile_image_url = upload_image.get_actual_url(image_url=user_profile_image_url, new_blob_container=BlobContainer.PROFILE_IMAGES.value, new_blob_name=f"profile-{db_user.uuid}") if user_profile_image_url is not None else None
        
    db.add(db_user)
    try:
        db.commit()
    except Exception as e:
        if user_profile_image_url is not None:
            upload_image.delete_blob_by_url(db_user.profile_image_url)
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id, models.User.is_archived == False).first()
    return user

def get_db_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id, models.User.is_archived == False).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email.ilike(email), models.User.is_archived == False).first()

def get_user_by_email_and_password(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email.ilike(email), models.User.is_archived == False).first()
    if user is None:
        return False
    if hashing.verify_password(password, user.hashed_password):
        return user
    return False

def get_users(db: Session, offset: int = 0, limit: int = 100):
    users = db.query(models.User).filter(models.User.role == 'organizer').offset(offset).limit(limit).all()
    return users

def update_user(db: Session, user: schemas.UserBaseUpdate, db_user: models.User):
    user_dict = user.model_dump()
    user_status = user_dict.pop("status")
    user_profile_image_url = user_dict.pop("profile_image_url")
    
    if user_status is not None:
        db_user.user_status_id = organizer.OrganizerEnum[user_status.upper()].value
    
    non_nullable_fields = ['first_name','last_name','business_type']

    for key, value in user_dict.items():
        if key in non_nullable_fields:
            if value is not None:
                setattr(db_user, key, value)
        else:
            setattr(db_user, key, value)

    if user_profile_image_url is not None and upload_image.get_container_name_from_url(user_profile_image_url) != BlobContainer.PROFILE_IMAGES.value:
        db_user.profile_image_url = upload_image.get_actual_url(image_url=user_profile_image_url, new_blob_container=BlobContainer.PROFILE_IMAGES.value, new_blob_name=f"profile-{db_user.uuid}")
    elif user_profile_image_url is None and db_user.profile_image_url is not None:
        upload_image.delete_blob_by_url(db_user.profile_image_url)
        db_user.profile_image_url = None

    db_user.updated_on = datetime.utcnow()
    try:
        db.commit()
    except Exception as e:
        if user_profile_image_url is not None:
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
    db_session = db.query(models.Session).filter(models.Session.owner_id == user.id).all()
    for session in db_session:
        session.is_archived = True
        
    conference = db.query(models.Conference).filter(models.Conference.owner_id == user.id).all()
    for c in conference:
        c.is_archived = True

    user.is_archived = True
    db.commit()
    return True