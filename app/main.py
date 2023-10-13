from fastapi import Depends, FastAPI, HTTPException
from .routers import ai_models, users, conferences, ai_models,sessions
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["https://localhost:3000/","https://localhost:3001/","https://localhost:3002/","https://conference-assitant-09086b978eb6.herokuapp.com/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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