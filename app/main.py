
from fastapi import Depends, FastAPI

from app.oauth2 import get_current_active_user
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

# Add the routers to the application with authentication middleware
app.include_router(users.router, dependencies=[Depends(get_current_active_user)])
app.include_router(conferences.router, dependencies=[Depends(get_current_active_user)])
app.include_router(sessions.router, dependencies=[Depends(get_current_active_user)])
app.include_router(settings.router, dependencies=[Depends(get_current_active_user)])
app.include_router(ai_models.router, dependencies=[Depends(get_current_active_user)])
app.include_router(authentication.router)

@app.get("/")
async def root():
    return {"message": "Conference Assistant API"}