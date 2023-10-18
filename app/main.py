from fastapi import Depends, FastAPI

from app.oauth2 import  get_current_active_user

from .routers import ai_models, users, conferences, ai_models, sessions, settings, authentication
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AuthenticationMiddleware = get_current_active_user()

# app.middleware<AuthenticationMiddleware>("http")(AuthenticationMiddleware)
    
app.include_router(users.router)
app.include_router(conferences.router)
app.include_router(sessions.router)
app.include_router(settings.router)
app.include_router(ai_models.router)
app.include_router(authentication.router)

@app.get("/")
async def root():
    return {"message": "Conference Assistant API"}