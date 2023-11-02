import csv
import json
from fastapi import APIRouter, Depends, UploadFile
import requests
from app.schemas import session_schemas as schemas
from app.dependencies import get_db
from app.file_upload import file_upload
from app.oauth2 import get_current_active_user, oauth_2_scheme
from app.routers.sessions import create_session_for_conference
from app.schemas.user_schemas import User
from ..data_ingestion import createVectorDb, file_path_in_files, find_delimiter
from ..data_query import query_document
from sqlalchemy.orm import Session
import pandas as pd
from datetime import date, time, datetime
from .. import models

router = APIRouter(tags=["ai_models"])

@router.post("/query_document")
async def query_document_endpoint(question: str, conference_id: str, current_user: User = Depends(get_current_active_user)):
    answer = query_document(question,conference_id)
    return {"answer": answer}

@router.post("/upload_session_file/")
async def upload_session_file(file: UploadFile,
                              conference_id: str,
                              current_user:User = Depends(get_current_active_user),
                              token: str = Depends(oauth_2_scheme),
                              db: Session = Depends(get_db)):
    response = file_upload(file, conference_id)
    file_path = file_path_in_files(conference_id)
    delimiters = [';', ',', '\t']
    delimiter = find_delimiter(file_path, delimiters)
    
    df = pd.read_csv(file_path, sep = delimiter)
    headers = df.columns.tolist()
    my_headers = ['name', 'start_time', 'end_time', 'location', 'date', 'description']
    
    if set(headers) != set(my_headers):
        return {"error": "The headers of the CSV file are not correct.",
                "expected headers": my_headers,
                "received headers": headers},        
    
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file, delimiter=delimiter)
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
    
    answer = response.copy()
    answer.update({"token": token, 'file_path': file_path, 'delimiter': delimiter})
    # createVectorDb(conference_id)
    return answer