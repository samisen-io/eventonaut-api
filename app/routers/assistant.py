from fastapi import APIRouter, Depends, HTTPException
from app.oauth2 import get_current_active_user
from .. import AI_assitant as assistant
from ..schemas import ai_assistant_schemas as schemas
import re

router = APIRouter(tags=["AI_assistant"])

@router.post("/assistant/create_assistant")
def create_assistant(schema: schemas.AssistantCreate):
    try:
        return assistant.create_assistant(schema=schema)
    except Exception as e:
        exception = str(e)
        hyphen_index = exception.find('-')
        error_code = int(re.search(r'\d+',exception[:hyphen_index].strip()).group())
        error_message = exception[hyphen_index+1:].strip()
        raise HTTPException(status_code=error_code, detail=error_message)
    
@router.get("/assistant/get_assistant/{assistant_id}")
def get_assistant(assistant_id: str):
    try:
        return assistant.get_assistant(assistant_id=assistant_id)
    except Exception as e:
        exception = str(e)
        hyphen_index = exception.find('-')
        error_code = int(re.search(r'\d+',exception[:hyphen_index].strip()).group())
        error_message = exception[hyphen_index+1:].strip()
        raise HTTPException(status_code=error_code, detail=error_message)
    
@router.put("/assistant/update_assistant")
def update_assistant(schema: schemas.AssistantUpdate):
    try:
        return assistant.update_assistant(schema=schema)
    except Exception as e:
        exception = str(e)
        hyphen_index = exception.find('-')
        error_code = int(re.search(r'\d+',exception[:hyphen_index].strip()).group())
        error_message = exception[hyphen_index+1:].strip()
        raise HTTPException(status_code=error_code, detail=error_message)
    
@router.delete("/assistant/delete_assistant/{assistant_id}")
def delete_assistant(assistant_id: str):
    try:
        return assistant.delete_assistant(assistant_id=assistant_id)
    except Exception as e:
        exception = str(e)
        hyphen_index = exception.find('-')
        error_code = int(re.search(r'\d+',exception[:hyphen_index].strip()).group())
        error_message = exception[hyphen_index+1:].strip()
        raise HTTPException(status_code=error_code, detail=error_message)

@router.get("/assistant/list_assistants")
def list_assistants():
    try:
        return assistant.list_assistants()
    except Exception as e:
        exception = str(e)
        hyphen_index = exception.find('-')
        error_code = int(re.search(r'\d+',exception[:hyphen_index].strip()).group())
        error_message = exception[hyphen_index+1:].strip()
        raise HTTPException(status_code=error_code, detail=error_message)