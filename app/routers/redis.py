from fastapi import APIRouter, HTTPException
from ..crud import redis_crud

router = APIRouter(tags=["redis"])

@router.get("/get-session/{session_id}")
async def get_session(key: str):
    session = redis_crud.get_session_from_redis(key)
    if session is None:
        raise HTTPException(status_code=404, detail=f"Session {key} not found")
    return session

@router.get("/get-list/{event_id}")
async def get_list(event_id: str):
    list_of_sessions = redis_crud.get_list_of_sessions_from_redis(event_id)
    if not list_of_sessions:
        raise HTTPException(status_code=404, detail=f"List of sessions for event {event_id} not found")
    return list_of_sessions

@router.post("/save-session")
async def save_session(key: str, value: dict):
    return redis_crud.save_session_to_redis(key, value)

@router.post("/save-list")
async def save_list(key: str, value: str):
    return redis_crud.save_list_of_sessions_to_redis(key, value)

@router.delete("/delete-session/{session_id}")
async def delete_session(key: str):
    return redis_crud.delete_data_from_redis(key)

@router.delete("/remove-session-from-list")
async def remove_session_from_list(key: str, value: str):
    return redis_crud.remove_session_from_list(key, value)

@router.get("/get-everything")
async def get_everything():
    return redis_crud.get_everything()