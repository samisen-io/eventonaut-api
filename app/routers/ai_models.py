from fastapi import APIRouter, Depends, UploadFile
from app.file_upload import file_upload
from app.oauth2 import get_current_active_user
from app.schemas.user_schemas import User
from ..data_ingestion import createVectorDb
from ..data_query import query_document
import os
import logging

router = APIRouter(tags=["ai_models"])

@router.post("/query_document")
async def query_document_endpoint(question: str, conference_id: str):
    answer = query_document(question,conference_id)
    return {"answer": answer}

@router.post("/upload_session_file/")
async def upload_session_file(file: UploadFile, conference_id: str):
    response = file_upload(file, conference_id)
    createVectorDb(conference_id)
    return response