from azure.storage.blob import BlobServiceClient,ContentSettings
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from dotenv import load_dotenv
import logging
import os
from ..basicauth import basic_auth
from uuid import uuid4

router = APIRouter(tags=["upload"])

load_dotenv()

@router.post("/upload_file", status_code=201)
def upload_file(file: UploadFile = File(...), basic_auth = Depends(basic_auth)):
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

        file_extension = file.filename.split(".")[-1]

        if file_extension not in ["jpg", "jpeg", "png"]: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only jpg, jpeg, and png are allowed.")

        blob_name = f"dyn-{uuid4()}.{file_extension}"
        blob_client = blob_service_client.get_blob_client("temporary-images", blob_name)

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
def get_containers(basic_auth = Depends(basic_auth)):
    try:
        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        containers = blob_service_client.list_containers()
        public_containers = [container.name for container in containers if container.public_access is not None]
        return {"containers": public_containers}
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ex))
    
def move_file_from_temporary_to_permanent_container(source_container_name, dest_container_name, old_blob_name, new_blob_name):
    try:
        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        source_blob_client = blob_service_client.get_blob_client(source_container_name, old_blob_name)
        dest_blob_client = blob_service_client.get_blob_client(dest_container_name, new_blob_name)
        dest_blob_client.start_copy_from_url(source_blob_client.url)
        source_blob_client.delete_blob()
        
        return dest_blob_client.url
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ex))
    
def delete_blob(container_name, blob_name):
    try:
        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_client = blob_service_client.get_blob_client(container_name, blob_name)
        blob_client.delete_blob()
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ex))    