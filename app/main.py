from fastapi import Depends, FastAPI
from app.oauth2 import get_current_active_user
from .routers import ai_models, users, conferences, ai_models, sessions, settings, attendee, agenda
from fastapi.middleware.cors import CORSMiddleware
from .routers import ai_models, users, conferences, ai_models, sessions, settings, authentication, otp, assistant

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the routers to the application with authentication middleware
app.include_router(users.router)
app.include_router(conferences.router)
app.include_router(sessions.router)
app.include_router(settings.router)
app.include_router(attendee.router)
app.include_router(agenda.router)
app.include_router(assistant.router)
app.include_router(otp.router)
app.include_router(ai_models.router, dependencies=[Depends(get_current_active_user)])
app.include_router(authentication.router)

@app.get("/")
async def root():
    return {"message": "Conference Assistant API"}