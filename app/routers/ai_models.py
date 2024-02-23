import ast
from datetime import date, datetime, time
import json
import sys
import logging
from fastapi import APIRouter, Depends, HTTPException, Security, UploadFile, status
from fastapi.responses import StreamingResponse
from app.crud.aitokens_crud import insert_aitoken
from app.crud.speakers_crud import get_speaker_uuid_by_email
from app.file_reader import read_file_return_csv
from app.schemas.venue_schemas import VenueResponse
from app.pinecone_operations import arranging_ouput_object, create_namespace, create_vector_db, delete_namespace, delete_vector_db
from app.routers.speakers import create_speaker
from app.schemas import aitokens_schemas as ait_schemas
from app.schemas import session_schemas as schemas
from app.schemas import speaker_schemas as speaker_schemas
from app.dependencies import get_db
from app.oauth2 import get_current_active_user
from app.routers.sessions import create_session_for_conference
from app.schemas.query_schema import QueryInput
from app.schemas.user_schemas import UserAuthentication as User
from app.static_enums.role import RoleEnum
from ..data_ingestion import add_documents, write_events_to_csv, write_sessions_to_csv, write_speakers_to_csv
from ..data_query import query_document, retrieve_answer_stream
from ..crud import conferences_crud, result_crud
from sqlalchemy.orm import Session
from app.schemas.user_schemas import UserAuthentication as User

router = APIRouter(tags=["ai_models"])

@router.put("/create_vector_db/", status_code=status.HTTP_201_CREATED)
async def create_index(name:str, current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name]), db: Session = Depends(get_db)):
    index_name = create_vector_db(name) 
    logging.info("Created index: " + index_name)  
    return {'index_name': index_name}

@router.delete("/delete_vector_db/")
async def delete_index(current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name]), db: Session = Depends(get_db)):
    status = delete_vector_db()
    logging.info("Deleted index: " + status)
    return status

@router.post("/query_the_document_stream/")
async def query_by_conference_id(query_input:QueryInput, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,])):
    conference_id = query_input.conference_id
    question = query_input.question
    conference = conferences_crud.get_conference_by_conference_uuid(db, conference_id)  
    if not conference:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    async def event_stream():
        async for chunk in retrieve_answer_stream(question,conference_id):
            if isinstance(chunk, list):
                source = chunk
                continue
            yield(chunk)
        yield ' #@!SAMISEN!@# '
        objects = result_crud.get_objects(db=db, objects=source)
        objects_dict = [{k: datetime_to_str(v) for k, v in obj.__dict__.items() if not k.startswith('_')} for obj in objects]
        json_data = json.dumps(objects_dict)
        final_result = arranging_ouput_object(json_data)
        yield final_result
    return StreamingResponse(event_stream())
    
@router.post("/query_the_document/")
async def query_by_conference_id(query_input:QueryInput, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ATTENDEE.name,])):
    start_time = datetime.utcnow()
    conference_id = query_input.conference_id
    question = query_input.question
    conference = conferences_crud.get_conference_by_conference_uuid(db, conference_id)  
    if not conference:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    data = query_document(question,conference_id)
    end_time = datetime.utcnow()
    processing_time = (end_time - start_time).total_seconds()
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
    for item in objects_dict:
        if 'venue_details' in item and isinstance(item['venue_details'], VenueResponse):
            item['venue_details'] = item['venue_details'].__dict__
    json_data = json.dumps(objects_dict)
    final_result = arranging_ouput_object(json_data)
    final_result = json.loads(final_result)
    final_result['answer'] = data['answer']
    final_result['processing_time'] = processing_time
    final_result['usage'] = data['usage']
    try:
        token = ait_schemas.AITokensCreate(**token_data)
    except Exception as e:
        logging.exception(str(e)+"\n"+str(token_data))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)+"\n"+str(token_data))
    insert_aitoken(db,token)
    logging.info("Query successfull")
    return final_result

@router.delete("/delete_namespace/")
async def delete_namespace_from_pinecone(conference_id: str, current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name]), db: Session = Depends(get_db)):
    conference = conferences_crud.get_conference_by_conference_uuid(db, conference_id)
    if not conference:
        logging.exception("Conference not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conference not found")
    stat = delete_namespace(conference_id)
    logging.info("Namespace deleted")
    return stat

@router.post("/upload_session_file/")
async def upload_session_file(file: UploadFile,
                              conference_id: str,
                              current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name]),
                              db: Session = Depends(get_db)):
    contents = await file.read()
    filename = file.filename
    reader = await read_file_return_csv(contents,filename)
    headers = reader.fieldnames
    reader = [{k.lower(): v for k, v in row.items()} for row in reader]
    my_headers = ['name', 'description', 'location', 'date', 'start_time', 'end_time', 'tags', 'speakers', 'status']
    if set(headers) != set(my_headers):
        error_message = {
            "error": "The attributes(Column Names) provided are not correct.", 
            "expected attributes(Column Names)": my_headers, 
            "received attributes(Column Names)": headers
        }
        logging.exception(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)  
    c=0
    for row in reader:
        speaker_emails = ast.literal_eval(row['speakers']) if row['speakers'] else None
        if speaker_emails:
            speaker_uuids = [get_speaker_uuid_by_email(db, email) for email in speaker_emails]
        else:
            speaker_uuids = None
        payload = {
            "name": f"{row['name']}" if row['name'] else None,
            "start_time": f"{row['start_time']}" if row['start_time'] else None,
            "end_time": f"{row['end_time']}" if row['end_time'] else None,
            "location": f"{row['location']}" if row['location'] else None,
            "date": f"{row['date']}" if row['date'] else None,
            "description": f"{row['description']}" if row['description'] else None,
            "conference_id": f"{conference_id}",
            "speakers": speaker_uuids,
            "tags": ast.literal_eval(row['tags']) if row['tags'] else None,
            "status": f"{row['status']}" if row['status'] else None
        }
        try:
            session = schemas.SessionCreate(**payload)
        except Exception as e:
            logging.exception(str(e)+"\n"+str(payload))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)+"\n"+str(payload))
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
    logging.info("Session file uploaded successfully")
    return {'filename': filename}

@router.post("/upload_speaker_file/")
async def upload_speaker_file(file: UploadFile,
                              conference_id: str,
                              current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name]),
                              db: Session = Depends(get_db)):
    contents = await file.read()
    filename = file.filename
    # read the file and return a csv reader object
    reader = await read_file_return_csv(contents,filename)
    headers = reader.fieldnames
    reader = [{k.lower(): v for k, v in row.items()} for row in reader]
    my_headers = ['name', 'title', 'bio','email']
    if set(headers) != set(my_headers):
        error_message = {
            "error": "The attributes(Column Names) provided are not correct.", 
            "expected attributes(Column Names)": my_headers, 
            "received attributes(Column Names)": headers
        }
        logging.exception(error_message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
    c=0
    for row in reader:
        payload = {
            "name": f"{row['name']}" if row['name'] else None,
            "title": f"{row['title']}" if row['title'] else None,
            "conference_id": f"{conference_id}",
            "bio": f"{row['bio']}" if row['bio'] else None,
            "email": f"{row['email']}" if row['email'] else None
        }
        try:
            speaker = speaker_schemas.SpeakerCreate(**payload)
        except Exception as e:
            logging.exception(str(e)+"\n"+str(payload))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)+"\n"+str(payload))
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
    logging.info("Speakers file uploaded successfully")
    return {'filename': filename}

@router.post("/synchronize_database_and_pinecone/")
async def update_namespace(conference_id: str, current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name]), db: Session = Depends(get_db)):
    write_sessions_to_csv(db,conference_id)
    write_speakers_to_csv(db,conference_id)
    write_events_to_csv(db,conference_id)
    namespace = create_namespace(conference_id)
    status = delete_namespace(conference_id)
    status = status['status']
    add_documents(namespace,conference_id,'sessions')
    add_documents(namespace,conference_id,'speakers')
    namespace = add_documents(namespace,conference_id,'events')
    namespace = namespace['namespace']
    logging.info("Database and Pinecone Synchronized")
    return {'namespace': namespace, 'deletion_status': status}

def datetime_to_str(dt):
    if isinstance(dt, date):
        return dt.strftime('%Y-%m-%d')
    elif isinstance(dt, time):
        return dt.strftime('%H:%M:%S')
    else:
        return dt