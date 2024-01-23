from azure.storage.blob import BlobServiceClient,ContentSettings
from fastapi import APIRouter, File, UploadFile, Depends, Security, HTTPException, status
from sqlalchemy.orm import Session
from ..dependencies import get_db
from app.oauth2 import get_current_active_user
from ..schemas.user_schemas import UserAuthentication as User
from ..crud import attendee_crud as crud
from dotenv import load_dotenv
import logging
import os

router = APIRouter(tags=["upload"])

load_dotenv()

@router.post("/upload_file", status_code=201)
def upload_file(container_name: str, file: UploadFile = File(...), current_user: User = Security(get_current_active_user, scopes=["attendee", "organizer"])):
    try:
        # Check file size
        file_size = len(file.file.read())
        max_file_size = 5 * 1024 * 1024  # 5 MB

        if file_size > max_file_size:
            logging.exception(f"The file size cannot exceed {max_file_size} bytes.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The file size cannot exceed {max_file_size} bytes.")

        file.file.seek(0)  # Reset file pointer to the beginning

        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        containers = blob_service_client.list_containers()
        public_containers = [container.name for container in containers if container.public_access is not None]
        if container_name not in public_containers:
            logging.exception(f"Invalid container name: {container_name}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid container name: {container_name}")
        container_client = blob_service_client.get_container_client(container_name)

        # # Create the container if it doesn't exist
        # try: 
        #     container_client.create_container()
        # except:
        #     pass  # The container already exists

        file_extension = file.filename.split(".")[-1]  # Get the file extension

        if file_extension not in ["jpg", "jpeg", "png"]: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only jpg, jpeg, and png are allowed.")

        blob_name = f"profile-{current_user.uuid}.{file_extension}"  # Append the file extension to the blob name
        blob_client = blob_service_client.get_blob_client(container_name, blob_name)

        content_settings = ContentSettings(content_type=f'image/{file_extension}')

        # Upload the image
        with file.file as data:
            blob_client.upload_blob(data, content_settings=content_settings, overwrite=True)

        # Get the image URL
        blob_url = blob_client.url
        return {"message": "Image uploaded successfully", "url": blob_url}

    except HTTPException as ex:
        raise HTTPException(status_code=ex.status_code, detail=ex.detail)
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ex))
    
@router.get("/get-containers")
def get_containers(current_user: User = Security(get_current_active_user, scopes=["attendee", "organizer"])):
    try:
        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        containers = blob_service_client.list_containers()
        public_containers = [container.name for container in containers if container.public_access is not None]
        return {"containers": public_containers}
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ex))