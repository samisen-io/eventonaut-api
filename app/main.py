from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import logging
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.routers import onesignal_push_notification
from .routers import signup_organizer
from .routers import backdrop_gallery, eventbrite_connector, organization, organization_user, photo_booth, role
from .routers import ai_models, users, conferences, ai_models, sessions, settings, attendee, agenda
from fastapi.middleware.cors import CORSMiddleware
from .routers import ai_models, users, conferences, ai_models, sessions, settings, authentication, otp, assistant, attendee_conference, client, speakers, promotions,sponsor, venue, static_organizer, static_client, static_event, static_session, static_attendee, upload_image, event_documents, session_documents, organization_settings, exhibitors, attendee_exhibitors, exhibitor_documents
from .crud import logout_token_crud


app = FastAPI()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# Start the scheduler
logout_token_crud.start_scheduler()

# app.middleware("http")(TimeoutMiddleware(app, 10))

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logging.exception(f"RequestValidationError: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": jsonable_encoder(exc.errors())}
    )
    
# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     logging.exception(f"HTTPException: {exc.detail}")
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.detail}
#     )
    
# @app.exception_handler(Exception)
# async def exception_handler(request: Request, exc: Exception):
#     logging.exception(f"Exception: {str(exc)}")
#     return JSONResponse(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         content={"detail": str(exc)}
#     )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add the routers to the application with authentication middleware
app.include_router(upload_image.router)
app.include_router(organization_settings.router)
app.include_router(signup_organizer.router)
app.include_router(organization.router)
app.include_router(organization_user.router)
app.include_router(role.router)
app.include_router(users.router)
app.include_router(client.router)
app.include_router(conferences.router)
app.include_router(backdrop_gallery.router)
app.include_router(venue.router)
app.include_router(speakers.router)
app.include_router(promotions.router)
app.include_router(sponsor.router)
app.include_router(sessions.router)
app.include_router(exhibitors.router)
app.include_router(exhibitor_documents.router)
app.include_router(settings.router)
# app.include_router(ai_models.router, dependencies=[Depends(get_current_active_user)])
app.include_router(ai_models.router)
app.include_router(photo_booth.router)
app.include_router(attendee.router)
app.include_router(attendee_conference.router)
app.include_router(agenda.router)
app.include_router(attendee_exhibitors.router)
app.include_router(assistant.router)
app.include_router(otp.router)
app.include_router(authentication.router)
app.include_router(event_documents.router)
app.include_router(session_documents.router)
app.include_router(static_organizer.router)
app.include_router(static_client.router)
app.include_router(static_event.router)
app.include_router(static_session.router)
app.include_router(static_attendee.router)
app.include_router(organization.router)
app.include_router(role.router)
app.include_router(eventbrite_connector.router)
app.include_router(onesignal_push_notification.router)

@app.get("/")
async def root():
    return {"message": "Conference Assistant API"}