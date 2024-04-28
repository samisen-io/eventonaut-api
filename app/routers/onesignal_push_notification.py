import os
from fastapi import APIRouter, Depends, Security, UploadFile
from app.edit_photo import check_the_file_size, check_the_file_type
from app.oauth2 import get_current_active_user
from app.onesignal_operations import create_notification
from app.schemas.user_schemas import UserAuthentication as User
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.routers.upload_image import upload_file
from app.static_enums.role import RoleEnum
from typing import Optional

router = APIRouter(tags=["onesignal_push_notification"])


@router.post("/send_notification")
def send_notification(conference_id: str,
                      message: str,
                      title: Optional[str] = None,  
                      picture: UploadFile = None,
                      current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, "organizer"]), 
                      db: Session = Depends(get_db)):
    event_logo_url = None
    if picture is not None:
        upload_file_response = upload_file(picture)
        event_logo_url = upload_file_response['url']            
    create_notification(db, conference_id, title, message, event_logo_url)
    return {'message': 'Notification sent successfully.'}
    