from azure.storage.blob import BlobServiceClient,ContentSettings
from fastapi import APIRouter, File, UploadFile, Depends, Security, HTTPException
from sqlalchemy.orm import Session
from .dependencies import get_db
from app.oauth2 import get_current_active_user
from .schemas.user_schemas import UserAuthentication as User
from .crud import attendee_crud as crud

router = APIRouter(tags=["image"])

@router.post("/upload_file")
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    try:
        connect_str = "DefaultEndpointsProtocol=https;AccountName=conferencebuddydev;AccountKey=AkI79mMDMpg+Xi75ez89PO5HuhqOLdB5cOtNhsARwapbPVcQ4AuzVkpJ7jaB+iIZm8WPV7HE4CSB+AStiZkq/A==;EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = "attende-profile-images"
        container_client = blob_service_client.get_container_client(container_name)

        # Create the container if it doesn't exist
        try: 
            container_client.create_container()
        except:
            pass  # The container already exists

        file_extension = file.filename.split(".")[-1]  # Get the file extension
        blob_name = f"profile-{current_user.uuid}.{file_extension}"  # Append the file extension to the blob name
        blob_client = blob_service_client.get_blob_client(container_name, blob_name)

        content_settings = ContentSettings(content_type=f'image/{file_extension}')

        # Upload the image
        with file.file as data:
            blob_client.upload_blob(data, content_settings=content_settings, overwrite=True)

        # Get the image URL
        blob_url = blob_client.url
        crud.update_attendee_image_url(db=db, attendee_id=current_user.id, image_url=blob_url)
        return {"message": "Image uploaded successfully", "url": blob_url}

    except Exception as ex:
        raise HTTPException(status_code=502, detail=str(ex))