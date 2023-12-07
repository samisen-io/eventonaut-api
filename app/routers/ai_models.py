import ast
import json
import sys
from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile
from app.file_reader import read_file_return_csv
from app.pinecone_operations import delete_vector_db
from app.schemas import session_schemas as schemas
from app.schemas import ai_assistant_schemas as ai_schemas
from app.dependencies import get_db
from app.oauth2 import get_current_active_user, oauth_2_scheme
from app.routers.sessions import create_session_for_conference
from app.schemas.query_schema import QueryInput
from app.schemas.user_schemas import UserAuthentication as User
from ..data_ingestion import create_vector_db, write_data_to_csv
from ..data_query import query_document
from ..crud import conferences_crud, attendee_crud
from sqlalchemy.orm import Session
from app.schemas.user_schemas import UserAuthentication as User

router = APIRouter(tags=["ai_models"])

@router.post("/query_the_document/")
async def query_document_using_conference_id(query_input:QueryInput, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    conference_id = query_input.conference_id
    question = query_input.question
    conference = conferences_crud.get_conference_by_conference_uuid(db, conference_id)  
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    data = query_document(question,conference_id)
    data = json.loads(data)
    return data

@router.delete("/delete_file/")
async def delete_file_from_openai(conference_id: str, current_user: User = Security(get_current_active_user, scopes=["organizer"]), db: Session = Depends(get_db)):
    conference = conferences_crud.get_conference_by_conference_uuid(db, conference_id)
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    index_name = delete_vector_db(conference_id)
    return {"success": "Sessions file deleted successfully.", "index_name": index_name}

@router.post("/database_and_repository_synchronization/")
async def update_conference(conference_id: str, current_user: User = Security(get_current_active_user, scopes=["organizer"]), db: Session = Depends(get_db)):
    write_data_to_csv(conference_id,db)
    delete_vector_db(conference_id)
    index_name = create_vector_db(conference_id)   
    return {'index_name': index_name}

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
            raise HTTPException(status_code=400, detail=str(e)+"\n"+str(payload))
        # upload to database
        create_session_for_conference(session,db,current_user)
        loading_chars = ['-', '\\', '|', '/']
        c = c + 1
        current_rows = c
        total_rows = len(reader)
        percentage_done = (current_rows / total_rows) * 100
        print('\r' + 'Loading: ' + loading_chars[c % len(loading_chars)] + f' {percentage_done:.2f}% done', end='')
        sys.stdout.flush()
    print()
    write_data_to_csv(conference_id,db)
    index_name = create_vector_db(conference_id)   
    return {'filename': filename, 'index_name': index_name}