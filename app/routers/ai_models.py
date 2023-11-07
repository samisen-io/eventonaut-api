from fastapi import APIRouter, Depends, HTTPException, UploadFile
from app.data_deletion import delete_collection
from app.file_reader import read_file_return_csv
from app.schemas import session_schemas as schemas
from app.dependencies import get_db
from app.file_upload import file_upload
from app.oauth2 import get_current_active_user, oauth_2_scheme
from app.routers.sessions import create_session_for_conference
from app.schemas.user_schemas import User
from ..data_ingestion import createVectorDb, write_data_to_csv
from ..data_query import query_document
from sqlalchemy.orm import Session

router = APIRouter(tags=["ai_models"])

def check_conference_id(conference_id):
    if int(conference_id) <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference id")
    
@router.post("/query_document")
async def query_document_endpoint(question: str, conference_id: str, current_user: User = Depends(get_current_active_user)):
    check_conference_id(conference_id)
    answer = query_document(question,conference_id)
    return {"answer": answer}

@router.post("/refresh_vectorDb/")
async def update_conference(conference_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    check_conference_id(conference_id)
    delete_collection(conference_id)
    write_data_to_csv(int(conference_id),db)
    createVectorDb(conference_id)
    return {"success": "Conference updated successfully."}

@router.delete("/delete_conference/")
async def delete_conference(conference_id: str, current_user: User = Depends(get_current_active_user)):
    check_conference_id(conference_id)
    delete_collection(conference_id)
    return {"success": "Conference deleted successfully."}

@router.post("/upload_session_file/")
async def upload_session_file(file: UploadFile,
                              conference_id: str,
                              current_user:User = Depends(get_current_active_user),
                              token: str = Depends(oauth_2_scheme),
                              db: Session = Depends(get_db)):
    # check if conference id is valid
    check_conference_id(conference_id)
    contents = await file.read()
    filename = file.filename
    # read the file and return a csv reader object
    reader = await read_file_return_csv(contents,filename)
    headers = reader.fieldnames
    my_headers = ['name', 'start_time', 'end_time', 'location', 'date', 'description']
    if set(headers) != set(my_headers):
        return {"error": "The headers of the CSV file are not correct.", "expected headers": my_headers, "received headers": headers},  
    for row in reader:
        payload = {
            "name": f"{row['name']}",
            "start_time": f"{row['start_time']}",
            "end_time": f"{row['end_time']}",
            "location": f"{row['location']}",
            "date": f"{row['date']}",
            "description": f"{row['description']}",
            "conference_id": f"{conference_id}"
        }
        session = schemas.SessionCreate(**payload)
        create_session_for_conference(session,db,current_user)
    write_data_to_csv(int(conference_id),db)
    createVectorDb(conference_id)
    return {'filename':file.filename}