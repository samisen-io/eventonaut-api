import ast
import os
import logging
from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile
from app.file_reader import read_file_return_csv
from app.schemas import session_schemas as schemas
from app.schemas import ai_assistant_schemas as ai_schemas
from app.dependencies import get_db
from app.file_upload import file_upload
from app.oauth2 import get_current_active_user, oauth_2_scheme
from app.routers.sessions import create_session_for_conference
from app.schemas.user_schemas import UserAuthentication as User
from ..data_ingestion import write_data_to_json
from ..data_query import query_document
from ..crud import conferences_crud, attendee_crud
from sqlalchemy.orm import Session
from ..AI_assitant import update_assistant, upload_file, delete_file
from app.schemas.user_schemas import UserAuthentication as User
from .. import basicauth

router = APIRouter(tags=["ai_models"])

@router.post("/query_document")
async def query_document_endpoint(question: str, conference_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    conference = conferences_crud.get_conference_by_conference_uuid(db, conference_id)
    if not conference:
        logging.exception("Conference not found")
        raise HTTPException(status_code=404, detail="Conference not found")
    assistant_id = conference.assistant_id
    thread_id = attendee_crud.get_thread_id_by_attendee_id(db, current_user.id)
    if not thread_id:
        logging.exception("Thread not found")
        raise HTTPException(status_code=404, detail="Thread not found")
    file_ids = conferences_crud.get_file_ids_by_conference_id(db, conference_id)
    if not file_ids:
        logging.exception("No files found for this conference")
        raise HTTPException(status_code=404, detail="No files found for this conference")
    answer = query_document(question,assistant_id,thread_id, file_ids)
    logging.info("Answer retrieved")
    return {"answer": answer}

@router.delete("/delete_file/")
async def delete_file_from_openai(conference_id: str, current_user: User = Security(get_current_active_user, scopes=["organizer"]), db: Session = Depends(get_db)):
    conference = conferences_crud.get_conference_by_conference_uuid(db, conference_id)
    if not conference:
        logging.exception("Conference not found")
        raise HTTPException(status_code=404, detail="Conference not found")
    assistant_id = conference.assistant_id
    file_ids = conferences_crud.get_file_ids_by_conference_id(db, conference_id)
    if not file_ids:
        logging.exception("No files found for this conference")
        raise HTTPException(status_code=404, detail="No files found for this conference")
    file_id = file_ids[0]
    # delete from openai assistant api and conference_files table
    try:
        delete_file(file_id=file_id)
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    conferences_crud.delete_file_id(db=db, file_id=file_id, conference_id=conference_id, owner_id=current_user.id)
    assistant_schema = create_assistant_schema(assistant_id, conference_id, file_id="")
    update_assistant(assistant_schema)
    # delete the file from the files folder
    file_path = os.path.join('app', 'files')
    file_path = os.path.join(file_path, 'sessions_'+str(conference_id)+'.json')
    os.remove(file_path)
    logging.info("File deleted")
    return {"success": "Sessions file deleted successfully."}

@router.post("/database_and_repository_synchronization/")
async def update_conference(conference_id: str, current_user: User = Security(get_current_active_user, scopes=["organizer"]), db: Session = Depends(get_db)):
    write_data_to_json(conference_id,db)
    file_ids = conferences_crud.get_file_ids_by_conference_id(db, conference_id)
    if file_ids:
        file_id = file_ids[0]
        # delete from openai assistant api
        try:
            delete_file(file_id=file_id)
        except Exception as e:
            logging.exception(str(e))
            raise HTTPException(status_code=400, detail=str(e))
        conferences_crud.delete_file_id(db=db, file_id=file_id, conference_id=conference_id, owner_id=current_user.id)
    filename = await upload_session_from_database(conference_id, current_user, db)
    logging.info("Database and repository synchronized")
    return filename

@router.post("/upload_session_file/")
async def upload_session_file(file: UploadFile,
                              conference_id: str,
                              current_user: User = Security(get_current_active_user, scopes=["organizer"]),
                              token: str = Depends(oauth_2_scheme),
                              db: Session = Depends(get_db)):
    contents = await file.read()
    filename = file.filename
    # read the file and return a csv reader object
    reader = await read_file_return_csv(contents,filename)
    headers = reader.fieldnames
    reader = [{k.lower(): v for k, v in row.items()} for row in reader]
    my_headers = ['name', 'description', 'location', 'date', 'start_time', 'end_time', 'tags', 'speakers']
    if set(headers) != set(my_headers):
        error_message = {
            "error": "The attributes(Column Names) provided are not correct.", 
            "expected attributes(Column Names)": my_headers, 
            "received attributes(Column Names)": headers
        }
        logging.exception(error_message)
        raise HTTPException(status_code=400, detail=error_message)  
    c=0
    for row in reader:
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
        try:
            session = schemas.SessionCreate(**payload)
        except Exception as e:
            logging.exception(str(e)+"\n"+str(payload))
            raise HTTPException(status_code=400, detail=str(e)+"\n"+str(payload))
        create_session_for_conference(session,db,current_user)
        c=c+1
        print(c)
    filename = await upload_session_from_database(conference_id, current_user, db)
    logging.info("Session file uploaded")
    return filename

# @router.post("/upload_sessions_from_database/")
async def upload_session_from_database(conference_id: str,
                                       current_user: User = Security(get_current_active_user, scopes=["organizer"]),
                                       db: Session = Depends(get_db)):
    write_data_to_json(conference_id,db)
    # get the file from the files folder
    file_path = os.path.join('app', 'files')
    file_path = os.path.join(file_path, 'sessions_'+str(conference_id)+'.json')
    try:
        file = upload_file(file_path)
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    try:
        conferences_crud.upload_file_id(db=db, file_id=file.id, conference_id=conference_id, owner_id=current_user.id)
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=f"Error uploading file: {str(e)}")
    try:
        assistant_id = conferences_crud.get_assistant_id_by_conference_id(db, conference_id)
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=f"Error getting assistant ID: {str(e)}")
    assistant_schema = create_assistant_schema(assistant_id, conference_id, file.id)
    update_assistant(assistant_schema)
    logging.info("Sessions uploaded from database")
    return {'filename':file.filename}

def create_assistant_schema(assistant_id, conference_id, file_id):
    payload = {
        "assistant_id": f"{assistant_id}",
        "model": "gpt-3.5-turbo-1106",
        "name": f"ca_{conference_id}",
        "description": "It's a conference assistant. it can help users with their queries related to the sessions of the conference to build their agenda/schedule.",
        "instructions": "You are conference assistant. You can help users with their queries related to the sessions of the conference to build their agenda/schedule.",
        "tools": [{"type": "code_interpreter"}],
        "file_ids": [f"{file_id}"],
        "metadata": {}
    }
    assistant = ai_schemas.AssistantUpdate(**payload)
    logging.info("Assistant schema created")
    return assistant