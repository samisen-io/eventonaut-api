import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os
from dotenv import load_dotenv
import logging

security = HTTPBasic()

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def basic_auth(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf-8")
    correct_username_bytes = client_id.encode("utf-8")
    is_username_correct = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )

    current_password_bytes = credentials.password.encode("utf-8")
    correct_password_bytes = client_secret.encode("utf-8")
    is_password_correct = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )

    if is_username_correct and is_password_correct:
        return True
    
    logging.error("Incorrect email or password")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Basic"},
    )