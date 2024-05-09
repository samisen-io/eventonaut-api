import io
from fastapi import APIRouter, File, HTTPException, Security, UploadFile, status
from PIL import Image
from fastapi.responses import StreamingResponse
from app.edit_photo import check_the_file_size, check_the_file_type, remove_background
from app.schemas.user_schemas import UserAuthentication as User
from app.oauth2 import get_current_active_user
from app.static_enums.role import RoleEnum
from rembg import remove

router = APIRouter(tags = ['photo_booth'])

@router.post('/remove_the_background_clipdrop/')
async def remove_the_background_using_clipdrop(file: UploadFile = File(...), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,])):
    try:
        file_object = file.file.read()
        check_the_file_size(file_object)
        check_the_file_type(file.filename)
        photo = remove_background(file_object, file.filename)
        image = Image.open(io.BytesIO(photo))
        byte_arr = io.BytesIO()
        image.save(byte_arr, format='PNG')
        response = StreamingResponse(io.BytesIO(byte_arr.getvalue()), media_type="image/png")
        response.headers["Content-Disposition"] = "attachment; filename=output.png"
        return response
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail) 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

@router.post('/remove_the_background/')
async def remove_the_background(file: UploadFile = File(...), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,])):
    try:
        file_object = file.file.read()
        check_the_file_size(file_object)
        check_the_file_type(file.filename)
        photo = remove(file_object)
        image = Image.open(io.BytesIO(photo))
        byte_arr = io.BytesIO()
        image.save(byte_arr, format='PNG')
        response = StreamingResponse(io.BytesIO(byte_arr.getvalue()), media_type="image/png")
        response.headers["Content-Disposition"] = "attachment; filename=output.png"
        return response
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail) 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))