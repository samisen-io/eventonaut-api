import ast
import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from app.data_deletion import delete_collection
from app.file_reader import read_file_return_csv
from app.schemas import session_schemas as schemas
from app.dependencies import get_db
from app.file_upload import file_upload
from app.oauth2 import get_current_active_user, oauth_2_scheme
from app.routers.sessions import create_session_for_conference
from app.schemas.user_schemas import User
from ..data_ingestion import createVectorDb, file_path_in_files, write_data_to_json
from ..data_query import query_document
from ..crud import conferences_crud, attendee_crud
from sqlalchemy.orm import Session
from ..AI_assitant import upload_file, delete_file

router = APIRouter(tags=["ai_models"])

@router.post("/query_document")
async def query_document_endpoint(question: str, attendee_id:str, conference_id: str, db: Session = Depends(get_db)):
    assistant_id = conferences_crud.get_conference_by_conference_uuid(db, conference_id).assistant_id
    thread_id = attendee_crud.get_attendee_by_uuid(db, attendee_id).thread_id
    file_ids= conferences_crud.get_file_ids_by_conference_id(db, conference_id)
    answer = query_document(question,assistant_id,thread_id, file_ids)
    return {"answer": answer}

@router.post("/refresh_input_file/")
async def update_conference(conference_id: str, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    write_data_to_json(conference_id,db)
    file_ids = conferences_crud.get_file_ids_by_conference_id(db, conference_id)
    file_id = file_ids[0]
    # delete from openai assistant api
    try:
        delete_file(file_id=file_id)
    except Exception as e:
        return HTTPException(status_code=400, detail=str(e))
    conferences_crud.delete_file_id(db=db, file_id=file_id, conference_id=conference_id, owner_id=current_user.id)
    # upload it into openai assistant api
    file_path = os.path.join('app', 'files')
    file_path = os.path.join(file_path, 'sessions_'+str(conference_id)+'.json')
    with open(file_path, 'rb') as file:
        try:
            file = upload_file(file)
        except:
            HTTPException(status_code=400, detail="File upload failed")
    conferences_crud.upload_file_id(db=db, file_id = file.id, conference_id=conference_id, owner_id=current_user.id)
    return {"success": "Conference updated successfully."}

@router.post("/upload_session_file/")
async def upload_session_file(file: UploadFile,
                              conference_id: str,
                              current_user:User = Depends(get_current_active_user),
                              token: str = Depends(oauth_2_scheme),
                              db: Session = Depends(get_db)):
    contents = await file.read()
    filename = file.filename
    # read the file and return a csv reader object
    reader = await read_file_return_csv(contents,filename)
    headers = reader.fieldnames
    my_headers = ['name', 'description', 'location', 'date', 'start_time', 'end_time', 'tags', 'speakers']
    if set(headers) != set(my_headers):
        return {"error": "The attributes(Column Names) provided are not correct.", "expected attributes(Column Names)": my_headers, "received attributes(Column Names)": headers},  
    for row in reader:
        # print("speakers before conversion", row['speakers'])
        payload = {
            "name": f"{row['name']}" if row['name'] else None,
            "start_time": f"{row['start_time']}" if row['start_time'] else None,
            "end_time": f"{row['end_time']}" if row['end_time'] else None,
            "location": f"{row['location']}" if row['location'] else None,
            "date": f"{row['date']}" if row['date'] else None,
            "description": f"{row['description']}" if row['description'] else None,
            "conference_id": f"{conference_id}",
            "speakers": ast.literal_eval(row['speakers']) if row['speakers'] else None,
            "tags": ast.literal_eval(row['tags']) if row['tags'] else None
        }
        session = schemas.SessionCreate(**payload)
        # create_session_for_conference(session,db,current_user)
    write_data_to_json(conference_id,db)
    # get the file from the files folder
    file_path = os.path.join('app', 'files')
    file_path = os.path.join(file_path, 'sessions_'+str(conference_id)+'.json')
    with open(file_path, 'rb') as file:
        file = upload_file(file)
    conferences_crud.upload_file_id(db=db, file_id = file.id, conference_id=conference_id, owner_id=current_user.id)
    return {'filename':file.filename}