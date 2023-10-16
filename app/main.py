from fastapi import Depends, FastAPI, HTTPException
from .routers import ai_models, users, conferences, ai_models, sessions, settings
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv()

CONFERENCE_PORTAL_LINKS = os.environ.get("CONFERENCE_PORTAL_LINKS").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CONFERENCE_PORTAL_LINKS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(conferences.router)
app.include_router(sessions.router)
app.include_router(settings.router)
app.include_router(ai_models.router)

@app.get("/")
async def root():
    return {"message": "Conference Assistant API"}