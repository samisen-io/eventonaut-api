from fastapi import Depends, FastAPI, HTTPException
from .routers import users, conferences


app = FastAPI()


app.include_router(users.router)
app.include_router(conferences.router)

@app.get("/")
async def root():
    return {"message": "Conference Assistant API"}

