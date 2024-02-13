from typing import Callable
from fastapi import Depends, FastAPI, Request, Response, APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.routing import APIRoute
from app.oauth2 import get_current_active_user
import logging
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from app.routers import organization, role
from .routers import ai_models, users, conferences, ai_models, sessions, settings, attendee, agenda
from fastapi.middleware.cors import CORSMiddleware
from .routers import ai_models, users, conferences, ai_models, sessions, settings, authentication, otp, assistant, attendee_conference, client, speakers, promotions,sponsor, venue, static_organizer, static_client, static_event, static_session, static_attendee, upload_image
from .crud import logout_token_crud

app = FastAPI()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Start the scheduler
logout_token_crud.start_scheduler()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": jsonable_encoder(exc.errors())}
    )

class CORSHandler(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def preflight_handler(request: Request) -> Response:
            logging.info(f"Request header: {request.headers}")
            if request.method == 'OPTIONS':
                logging.info("Entered into OPTIONS")
                response = Response()
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'POST, GET, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
                logging.info(response)
            else:
                response = await original_route_handler(request)

        return preflight_handler

options_router = APIRouter(route_class=CORSHandler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the routers to the application with authentication middleware
app.include_router(options_router)
app.include_router(upload_image.router)
app.include_router(users.router)
app.include_router(client.router)
app.include_router(conferences.router)
app.include_router(venue.router)
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
app.include_router(static_organizer.router)
app.include_router(static_client.router)
app.include_router(static_event.router)
app.include_router(static_session.router)
app.include_router(static_attendee.router)
app.include_router(organization.router)
app.include_router(role.router)

@app.get("/")
async def root():
    return {"message": "Conference Assistant API"}