from fastapi import Depends, FastAPI
from app.oauth2 import get_current_active_user
import logging
from .routers import ai_models, users, conferences, ai_models, sessions, settings, attendee, agenda
from fastapi.middleware.cors import CORSMiddleware
from .routers import ai_models, users, conferences, ai_models, sessions, settings, authentication, otp, assistant, attendee_conference, client, speakers, promotions,sponsor
from . import upload_image
from .crud import logout_token_crud

app = FastAPI()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Start the scheduler
logout_token_crud.start_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the routers to the application with authentication middleware
app.include_router(upload_image.router)
app.include_router(users.router)
app.include_router(client.router)
app.include_router(conferences.router)
app.include_router(speakers.router)
app.include_router(promotions.router)
app.include_router(sponsor.router)
app.include_router(sessions.router)
app.include_router(settings.router)
# app.include_router(ai_models.router, dependencies=[Depends(get_current_active_user)])
app.include_router(ai_models.router)
app.include_router(attendee.router)
app.include_router(attendee_conference.router)
app.include_router(agenda.router)
app.include_router(assistant.router)
app.include_router(otp.router)
app.include_router(authentication.router)

@app.get("/")
async def root():
    return {"message": "Conference Assistant API"}