import ast
from datetime import date, datetime, time, timezone
import json
import sys
from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile
from app.crud.aitokens_crud import insert_aitoken
from app.file_reader import read_file_return_csv
from app.pinecone_operations import arranging_ouput_object, create_vector_db, delete_namespace, delete_vector_db
from app.routers.speakers import create_speaker
from app.schemas import aitokens_schemas as ait_schemas
from app.schemas import session_schemas as schemas
from app.schemas import speaker_schemas as speaker_schemas
from app.schemas import ai_assistant_schemas as ai_schemas
from app.dependencies import get_db
from app.oauth2 import get_current_active_user, oauth_2_scheme
from app.routers.sessions import create_session_for_conference
from app.schemas.query_schema import QueryInput
from app.schemas.user_schemas import UserAuthentication as User
from ..data_ingestion import add_documents, write_events_to_csv, write_sessions_to_csv, write_speakers_to_csv
from ..data_query import query_document
from ..crud import conferences_crud, result_crud
from sqlalchemy.orm import Session
from app.schemas.user_schemas import UserAuthentication as User

router = APIRouter(tags=["ai_models"])

@router.put("/create_vector_db/")
async def create_index(name:str, current_user: User = Security(get_current_active_user, scopes=["organizer"]), db: Session = Depends(get_db)):
    index_name = create_vector_db(name)   
    return {'index_name': index_name}

@router.delete("/delete_vector_db/")
async def delete_index(current_user: User = Security(get_current_active_user, scopes=["organizer"]), db: Session = Depends(get_db)):
    status = delete_vector_db()
    return status

@router.post("/query_the_document/")
async def query_by_conference_id(query_input:QueryInput, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["attendee"])):
    start_time = datetime.utcnow()
    conference_id = query_input.conference_id
    question = query_input.question
    conference = conferences_crud.get_conference_by_conference_uuid(db, conference_id)  
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    data = query_document(question,conference_id)
    end_time = datetime.utcnow()
    # return end_time-start_time
    processing_time = (end_time - start_time).total_seconds()
    # return processing_time
    data = json.loads(data)
    token_data = {
        'conference_id' : conference_id,
        'attendee_id' : current_user.uuid,
        'successful_requests' : data['usage']['successful_requests'],
        'total_cost' : data['usage']['total_cost'],
        'total_tokens' : data['usage']['total_tokens'],
        'prompt_tokens' : data['usage']['prompt_tokens'],
        'completion_tokens' : data['usage']['completion_tokens'],
        'processing_time' : processing_time
    }
    data['processing_time']=processing_time
    objects = result_crud.get_objects(db=db, objects=data['source_list'])
    objects_dict = [{k: datetime_to_str(v) for k, v in obj.__dict__.items() if not k.startswith('_')} for obj in objects]
    json_data = json.dumps(objects_dict)
    final_result = arranging_ouput_object(json_data)
    final_result = json.loads(final_result)
    final_result['answer'] = data['answer']
    final_result['processing_time'] = processing_time
    final_result['usage'] = data['usage']
    try:
        token = ait_schemas.AITokensCreate(**token_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)+"\n"+str(token_data))
    insert_aitoken(db,token)
    return final_result

@router.delete("/delete_file/")
async def delete_file_from_openai(conference_id: str, current_user: User = Security(get_current_active_user, scopes=["organizer"]), db: Session = Depends(get_db)):
    conference = conferences_crud.get_conference_by_conference_uuid(db, conference_id)
    if not conference:
        raise HTTPException(status_code=404, detail="Conference not found")
    status = delete_namespace(conference_id)
    return status

@router.post("/upload_session_file/")
async def upload_session_file(file: UploadFile,
                              conference_id: str,
                              current_user: User = Security(get_current_active_user, scopes=["organizer"]),
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
    return {'filename': filename}

@router.post("/upload_speaker_file/")
async def upload_speaker_file(file: UploadFile,
                              conference_id: str,
                              current_user: User = Security(get_current_active_user, scopes=["organizer"]),
                              db: Session = Depends(get_db)):
    contents = await file.read()
    filename = file.filename
    # read the file and return a csv reader object
    reader = await read_file_return_csv(contents,filename)
    headers = reader.fieldnames
    reader = [{k.lower(): v for k, v in row.items()} for row in reader]
    my_headers = ['name', 'title', 'bio']
    if set(headers) != set(my_headers):
        error_message = {
            "error": "The attributes(Column Names) provided are not correct.", 
            "expected attributes(Column Names)": my_headers, 
            "received attributes(Column Names)": headers
        }
        raise HTTPException(status_code=400, detail=error_message)  
    print(headers)
    c=0
    for row in reader:
        payload = {
            "name": f"{row['name']}" if row['name'] else None,
            "title": f"{row['title']}" if row['title'] else None,
            "conference_id": f"{conference_id}",
            "bio": f"{row['bio']}" if row['bio'] else None,
        }
        try:
            speaker = speaker_schemas.SpeakerCreate(**payload)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)+"\n"+str(payload))
        # upload to database
        create_speaker(speaker,db,current_user)
        loading_chars = ['-', '\\', '|', '/']
        c = c + 1
        current_rows = c
        total_rows = len(reader)
        percentage_done = (current_rows / total_rows) * 100
        print('\r' + 'Loading: ' + loading_chars[c % len(loading_chars)] + f' {percentage_done:.2f}% done', end='')
        sys.stdout.flush()
    print()
    return {'filename': filename}

@router.post("/synchronize_database_and_pinecone/")
async def update_namespace(conference_id: str, current_user: User = Security(get_current_active_user, scopes=["organizer"]), db: Session = Depends(get_db)):
    write_sessions_to_csv(db,conference_id)
    write_speakers_to_csv(db,conference_id)
    write_events_to_csv(db,conference_id)
    status = delete_namespace(conference_id)
    status = status['status']
    add_documents(conference_id,'sessions')
    add_documents(conference_id,'speakers')
    namespace = add_documents(conference_id,'events')
    namespace = namespace['namespace']
    return {'namespace': namespace, 'deletion_status': status}

def datetime_to_str(dt):
    if isinstance(dt, date):
        return dt.strftime('%Y-%m-%d')
    elif isinstance(dt, time):
        return dt.strftime('%H:%M:%S')
    else:
        return dt