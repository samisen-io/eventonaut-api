from fastapi import APIRouter, HTTPException, Depends, Header, Security
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.schemas.user_schemas import UserAuthentication as User
from app.oauth2 import get_current_active_user
from ..schemas import conference_schemas as schemas
from ..schemas import user_schemas as uschemas
from ..crud import conferences_crud as crud, users_crud, client_crud
from ..dependencies import get_db
from .. import basicauth
from datetime import date
import qrcode
import io
import json

router = APIRouter(tags=["conferences"])

# create conference
@router.post("/conferences", response_model=schemas.Conference)
def create_conference_for_user(conference: schemas.ConferenceCreate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    if current_user.id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user id")
    if not users_crud.get_user(db, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="User not found")
    if conference.start_date > conference.end_date or conference.start_date < date.today():
        raise HTTPException(status_code=400, detail="Invalid date range")
    return crud.create_user_conference(db=db, conference=conference, user_id=current_user.id)

# get all conferences
@router.get("/conferences/all_conferences", response_model=list[schemas.Conference])
def get_all_conferences(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if offset < 0 or limit < 0:
        raise HTTPException(status_code=400, detail="Invalid query parameters")
    conferences = crud.get_all_conferences(db, offset=offset, limit=limit)
    if conferences is None or len(conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return conferences

# get all conferences for attendee
@router.get("/conferences/for_attendee", response_model=list[schemas.Conference])
def get_all_conferences_for_attendee(offset: int = 0, limit: int = 100, db: Session = Depends(get_db),basic_auth = Depends(basicauth.basic_auth)):
    if offset < 0 or limit < 0:
        raise HTTPException(status_code=400, detail="Invalid query parameters")
    conferences = crud.get_all_conferences_for_attendee(db, offset=offset, limit=limit)
    if conferences is None or len(conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return conferences

# get all conferences by owner_id
@router.get("/conferences", response_model=list[schemas.Conference])
def get_all_conferences_by_owner_id(db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    if current_user.id <= 0:
        raise HTTPException(status_code=400, detail="Invalid owner id")
    if users_crud.get_user(db, user_id=current_user.id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_conferences = crud.get_conferences_by_owner_id(db, owner_id=current_user.id)
    if db_conferences is None or len(db_conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

# update conference by conference id
@router.put("/conferences", response_model=schemas.Conference)
def update_conference(conference: schemas.ConferenceUpdate, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    if all(value is None for value in dict(conference).values()):
        raise HTTPException(status_code=400, detail="Invalid request body")
    db_conference = crud.get_conference_by_uuid(db, uuid=conference.id, owner_id=current_user.id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    if conference.start_date is not None and conference.end_date is not None:
        if conference.start_date > conference.end_date or conference.start_date < date.today():
            raise HTTPException(status_code=400, detail="Invalid date range")
    if conference.client_id is not None:
        if not client_crud.get_client_by_uuid(db, client_uuid=conference.client_id):
            raise HTTPException(status_code=404, detail="Client not found")
    return crud.update_user_conference(db=db, conference=conference, uuid=conference.id, owner_id=current_user.id)

# delete conference
@router.delete("/conferences/{conference_id}")
def delete_conference_owner_id_conference_id(conference_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    if current_user.id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id")
    if not users_crud.get_user(db, user_id=current_user.id):
        raise HTTPException(status_code=404, detail="User not found")
    db_conference = crud.get_conference_by_uuid(db,owner_id=current_user.id, uuid=conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return crud.delete_conference(db=db, owner_id=current_user.id, uuid=conference_id)

# generate qr code based on conference uuid
@router.get("/conferences/generate_qr_code/{conference_id}")
def generate_qr_code(conference_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=["organizer"])):
    conference = crud.get_conference_by_uuid(db, uuid=conference_id, owner_id=current_user.id)
    if conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr_data = {
        "conference_id": conference.uuid,
        "conference_name": conference.name,
        "conference_code": conference.code
    }

    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr)
    img_byte_arr.seek(0)

    headers = {
        "Content-Disposition": f"attachment; filename=conf_qrcode.png",
    }

    return StreamingResponse(img_byte_arr, media_type="image/png", headers=headers)