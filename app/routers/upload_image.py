from urllib.parse import urlparse, unquote
from azure.storage.blob import BlobServiceClient,ContentSettings
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, status
from dotenv import load_dotenv
import logging
import os
from ..basicauth import basic_auth
from uuid import uuid4
from ..static_enums.blob_container_enums import BlobContainer

router = APIRouter(tags=["upload"])

load_dotenv()

@router.post("/upload_file", status_code=201)
def upload_file(file: UploadFile = File(...), basic_auth = Depends(basic_auth)):
    try:
        file_size = len(file.file.read())
        max_file_size_mb = 5  # 5 MB
        max_file_size = max_file_size_mb * 1024 * 1024

        if file_size > max_file_size:
            logging.exception(f"The file size cannot exceed {max_file_size_mb} MB")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The file size cannot exceed {max_file_size_mb} MB")  

        file.file.seek(0)  # Reset file pointer to the beginning

        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        file_extension = file.filename.split(".")[-1]

        executable_extensions = ["exe", "dll", "bat", "sh", "jar", "msi", "bin", "cmd", "apk", "app", "cgi", "com", "gadget", "pif", "wsf"]
        
        blob_client = None
        
        if file_extension in executable_extensions:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Executable files are not allowed.")

        elif file_extension in ["jpg", "jpeg", "png"]: 
            blob_name = f"dyn-{uuid4()}-{file.filename}"
            blob_client = blob_service_client.get_blob_client("temporary-images", blob_name)

            content_settings = ContentSettings(content_type=f'image/{file_extension}')

        elif file_extension in ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv"]:
            blob_name = file.filename
            if file.filename[:3] == "evt":
                blob_client = blob_service_client.get_blob_client(BlobContainer.EVENT_DOCUMENTS.value, blob_name)
            elif file.filename[:3] == "ses":
                blob_client = blob_service_client.get_blob_client(BlobContainer.SESSION_DOCUMENTS.value, blob_name)
            
            if file_extension in ['txt', 'csv']:
                content_settings = ContentSettings(content_type=f'text/{file_extension}')
            else:
                content_settings = ContentSettings(content_type=f'application/{file_extension}')
                
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type")
                                
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
    
@router.get("/get-containers", include_in_schema=False)
def get_containers(basic_auth = Depends(basic_auth)):
    try:
        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        containers = blob_service_client.list_containers()
        public_containers = [container.name for container in containers if container.public_access is not None]
        return {"containers": public_containers}
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ex))

def get_blob_by_url(blob_url):
    try:
        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        url = urlparse(blob_url)
        container_name = unquote(url.path.split("/")[1])
        blob_name = unquote(url.path.split("/")[2])
        
        blob_client = blob_service_client.get_blob_client(container_name, blob_name)
        
        return blob_client
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ex))

def check_for_blob_in_container(blob_url, container_name):
    try:
        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        blob_name = blob_url.split("/")[-1]
        blob_client = blob_service_client.get_blob_client(container_name, blob_name)
        if blob_client.exists():
            return True
        return False
    except Exception as ex:
        logging.exception(str(ex))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ex))
    
def get_actual_url(image_url:str, new_blob_container:str, new_blob_name:str):
    parsed_url = urlparse(image_url)
    path = parsed_url.path
    filename_with_ext = os.path.basename(path)
    _, extension = os.path.splitext(filename_with_ext)

    if extension not in ['.jpg', '.jpeg', '.png']:
        logging.exception("Invalid image file format")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file format")
    
    return move_file_from_temporary_to_permanent_container(source_container_name="temporary-images", dest_container_name = new_blob_container, old_blob_name = filename_with_ext, new_blob_name = new_blob_name + extension)
    
def move_file_from_temporary_to_permanent_container(source_container_name, dest_container_name, old_blob_name, new_blob_name):
    try:
        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        source_blob_client = blob_service_client.get_blob_client(source_container_name, unquote(old_blob_name))
        dest_blob_client = blob_service_client.get_blob_client(dest_container_name, unquote(new_blob_name))
        dest_blob_client.start_copy_from_url(source_blob_client.url)
        source_blob_client.delete_blob()
        
        logging.info(f"Blob {old_blob_name} moved to {dest_container_name} container successfully")
        return dest_blob_client.url
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(ex))
 
def get_container_name_from_url(blob_url):
    url = urlparse(blob_url)
    return unquote(url.path.split("/")[1])
    
def delete_blob_by_url(blob_url):
    try:
        connect_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        url = urlparse(blob_url)
        container_name = unquote(url.path.split("/")[1])
        blob_name = unquote(url.path.split("/")[2])
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        if not blob_client.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        
        blob_client.delete_blob()
        
        logging.info(f"Blob {blob_name} deleted successfully")
    except Exception as ex:
        logging.exception(str(ex))
        if hasattr(ex, 'status_code'):

            raise HTTPException(status_code=ex.status_code, detail=str(ex.detail))
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ex))