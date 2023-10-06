from fastapi import Depends, FastAPI, HTTPException
from .routers import ai_models, users, conferences, ai_models


app = FastAPI()


app.include_router(users.router)
app.include_router(conferences.router)
app.include_router(ai_models.router)

@app.get("/")
async def root():
    return {"message": "Conference Assistant API"}

