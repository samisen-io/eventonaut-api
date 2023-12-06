from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from fastapi import APIRouter, File, UploadFile

router = APIRouter(tags=["image"])


@router.post("/upload_image")
def upload_image(file: UploadFile = File(...)):
    try:
        connect_str = "DefaultEndpointsProtocol=https;AccountName=conferencebuddydev;AccountKey=AkI79mMDMpg+Xi75ez89PO5HuhqOLdB5cOtNhsARwapbPVcQ4AuzVkpJ7jaB+iIZm8WPV7HE4CSB+AStiZkq/A==;EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = "attendee-profile-images"
        blob_name = f"profile-image-{file.filename}" #profile-(attendee_id)
        blob_client = blob_service_client.get_blob_client(container_name, blob_name)

        # Upload the image
        with open("<your-image-path>", "rb") as data:
            blob_client.upload_blob(data)
        
        # get the image url
        blob_url = blob_client.url
        return {"message": "Image uploaded successfully", "url": blob_url}

    except Exception as ex:
        print('Exception:')
        print(ex)