import os
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile
from app.crud.conferences_crud import get_conference_by_uuid
from app.edit_photo import check_the_file_size, check_the_file_type
from app.oauth2 import get_current_active_user
from app.onesignal_operations import create_notification
from app.schemas.onesignal_notification_schema import PushNotification
from app.schemas.user_schemas import UserAuthentication as User
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.routers.upload_image import upload_file
from app.static_enums.role import RoleEnum
from typing import Optional

router = APIRouter(tags=["onesignal_push_notification"])


@router.post("/send_notification")
def send_notification(notification: PushNotification, 
                      current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"]),
                      db: Session = Depends(get_db)):
    conference_id = notification.conference_id
    message = notification.message
    title = notification.title
    picture_url = notification.picture
    if get_conference_by_uuid(db,conference_id, current_user.id) is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if not title:
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    if not is_valid_url(picture_url):
        raise HTTPException(status_code=400, detail="Invalid URL")
    create_notification(db, conference_id, title, message, picture_url)
    return {'message': 'Notification sent successfully.'}
    
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False
    
    