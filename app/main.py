from fastapi import Depends, FastAPI, HTTPException
from .routers import ai_models, users, conferences, ai_models,sessions
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], #TODO: Change this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(conferences.router)
app.include_router(sessions.router)
app.include_router(ai_models.router)

@app.get("/")
async def root():
    return {"message": "Conference Assistant API"}