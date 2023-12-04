from fastapi import APIRouter, Depends, HTTPException
import logging
from .. import AI_assitant
from ..schemas import ai_assistant_schemas as schemas
from .. import basicauth
import re

router = APIRouter(tags=["AI_assistant"])

@router.post("/assistant/create_assistant")
def create_assistant(schema: schemas.AssistantCreate, basic_auth = Depends(basicauth.basic_auth)):
    try:
        assistant = AI_assitant.create_assistant(schema=schema)
        logging.info("Assistant created: " + schema.name)
        return assistant
    except Exception as e:
        exception = str(e)
        hyphen_index = exception.find('-')
        error_code = int(re.search(r'\d+',exception[:hyphen_index].strip()).group())
        error_message = exception[hyphen_index+1:].strip()
        logging.error(error_message)
        raise HTTPException(status_code=error_code, detail=error_message)
    
@router.get("/assistant/get_assistant/{assistant_id}")
def get_assistant(assistant_id: str, basic_auth = Depends(basicauth.basic_auth)):
    try:
        assistant = AI_assitant.get_assistant(assistant_id=assistant_id)
        logging.info("Assistant retrieved: " + assistant.name)
        return assistant
    except Exception as e:
        exception = str(e)
        hyphen_index = exception.find('-')
        error_code = int(re.search(r'\d+',exception[:hyphen_index].strip()).group())
        error_message = exception[hyphen_index+1:].strip()
        logging.error(error_message)
        raise HTTPException(status_code=error_code, detail=error_message)
    
@router.put("/assistant/update_assistant")
def update_assistant(schema: schemas.AssistantUpdate, basic_auth = Depends(basicauth.basic_auth)):
    try:
        updated_assistant = AI_assitant.update_assistant(schema=schema)
        logging.info("Assistant updated: " + schema.name)
        return updated_assistant
    except Exception as e:
        exception = str(e)
        hyphen_index = exception.find('-')
        error_code = int(re.search(r'\d+',exception[:hyphen_index].strip()).group())
        error_message = exception[hyphen_index+1:].strip()
        logging.error(error_message)
        raise HTTPException(status_code=error_code, detail=error_message)
    
@router.delete("/assistant/delete_assistant/{assistant_id}")
def delete_assistant(assistant_id: str, basic_auth = Depends(basicauth.basic_auth)):
    try:
        delete_assistant = AI_assitant.delete_assistant(assistant_id=assistant_id)
        logging.info("Assistant deleted: " + assistant_id)
        return delete_assistant
    except Exception as e:
        exception = str(e)
        hyphen_index = exception.find('-')
        error_code = int(re.search(r'\d+',exception[:hyphen_index].strip()).group())
        error_message = exception[hyphen_index+1:].strip()
        logging.error(error_message)
        raise HTTPException(status_code=error_code, detail=error_message)

@router.get("/assistant/list_assistants")
def list_assistants(basic_auth = Depends(basicauth.basic_auth)):
    try:
        assistant_list = AI_assitant.list_assistants()
        logging.info("Assistants retrieved")
        return assistant_list
    except Exception as e:
        exception = str(e)
        hyphen_index = exception.find('-')
        error_code = int(re.search(r'\d+',exception[:hyphen_index].strip()).group())
        error_message = exception[hyphen_index+1:].strip()
        logging.error(error_message)
        raise HTTPException(status_code=error_code, detail=error_message)