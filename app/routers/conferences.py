from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ..schemas import conference_schemas as schemas
from ..crud import conferences_crud as crud, users_crud
from ..dependencies import get_db
from datetime import date

router = APIRouter(tags=["conferences"])

# create conference
@router.post("/conferences/{user_id}", response_model=schemas.Conference)
def create_conference_for_user(user_id: int, conference: schemas.ConferenceCreate, db: Session = Depends(get_db)):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user id")
    if not users_crud.get_user(db, user_id=user_id):
        raise HTTPException(status_code=404, detail="User not found")
    if conference.start_date > conference.end_date:
        raise HTTPException(status_code=400, detail="Invalid date range")
    return crud.create_user_conference(db=db, conference=conference, user_id=user_id)

# get all conferences
@router.get("/conferences/", response_model=list[schemas.Conference])
def get_all_conferences(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    if skip < 0 or limit < 0:
        raise HTTPException(status_code=400, detail="Invalid query parameters")
    conferences = crud.get_conferences(db, skip=skip, limit=limit)
    if conferences is None or len(conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return conferences

# get conference by conference id
@router.get("/conferences/{conference_id}", response_model=schemas.Conference)
def get_conference_by_conference_id(conference_id: int, db: Session = Depends(get_db)):
    if conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference id")
    db_conference = crud.get_conference(db, conference_id=conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference

# get all conferences by conference name
@router.get("/conferences/name/{name}", response_model=list[schemas.Conference])
def get_all_conferences_by_conference_name(name: str, db: Session = Depends(get_db)):
    if name.isnumeric():
        raise HTTPException(status_code=400, detail="Invalid conference name")
    db_conference = crud.get_conferences_by_name(db, name=name)
    if db_conference is None or len(db_conference) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference

# get all conferences by location
@router.get("/conferences/location/{location}", response_model=list[schemas.Conference])
def get_all_conferences_by_location(location: str, db: Session = Depends(get_db)):
    if location.isnumeric():
        raise HTTPException(status_code=400, detail="Invalid conference name")
    db_conference = crud.get_conferences_by_location(db, location=location)
    if db_conference is None or len(db_conference) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference

# get all conferences by start_date
@router.get("/conferences/start_date/{start_date}", response_model=list[schemas.Conference])
def get_all_conferences_by_start_date(start_date: date, db: Session = Depends(get_db)):
    db_conferences = crud.get_conferences_by_start_date(db, start_date=start_date)
    if db_conferences is None or len(db_conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

# get all conferences by end_date
@router.get("/conferences/end_date/{end_date}", response_model=list[schemas.Conference])
def get_all_conferences_by_end_date(end_date: date, db: Session = Depends(get_db)):
    db_conferences = crud.get_conferences_by_end_date(db, end_date=end_date)
    if db_conferences is None or len(db_conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

# get all conferences by description
@router.get("/conferences/description/{description}", response_model=list[schemas.Conference])
def get_all_conferences_by_description(description: str, db: Session = Depends(get_db)):
    if description.isnumeric():
        raise HTTPException(status_code=400, detail="Invalid conference name")
    db_conference = crud.get_conferences_by_description(db, description=description)
    if db_conference is None or len(db_conference) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference

# get conference by owner id and conference id
@router.get("/conferences/owner_id/{owner_id}/conference/{conference_id}", response_model=schemas.Conference)
def get_conference_by_owner_id_conference_id(owner_id: int, conference_id: int, db: Session = Depends(get_db)):
    if owner_id <= 0 or conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id or conference id")
    if users_crud.get_user(db, user_id=owner_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_conference = crud.get_conference_by_owner_id(db, owner_id=owner_id, conference_id=conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conference

# get all conferences by owner_id by name
@router.get("/conferences/owner/{owner_id}/name/{name}", response_model=list[schemas.Conference])
def get_all_conferences_owner_id_by_name(owner_id: int, name: str, db: Session = Depends(get_db)):
    if name.isnumeric() or owner_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference name or owner id")
    if users_crud.get_user(db, user_id=owner_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_conferences = crud.get_conferences_owner_id_by_name(db, name=name, owner_id=owner_id)
    if db_conferences is None or len(db_conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

# get all conferences by owner_id by location
@router.get("/conferences/owner/{owner_id}/location/{location}", response_model=list[schemas.Conference])
def get_all_conferences_owner_id_by_location(owner_id: int, location: str, db: Session = Depends(get_db)):
    if location.isnumeric() or owner_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference name or owner id")
    if users_crud.get_user(db, user_id=owner_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_conferences = crud.get_conferences_owner_id_by_location(db, location=location, owner_id=owner_id)
    if db_conferences is None or len(db_conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

# get all conferences by owner_id by start_date
@router.get("/conferences/owner/{owner_id}/start_date/{start_date}", response_model=list[schemas.Conference])
def get_all_conferences_owner_id_by_start_date(owner_id: int, start_date: date, db: Session = Depends(get_db)):
    if owner_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid owner id")
    if users_crud.get_user(db, user_id=owner_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_conferences = crud.get_conferences_owner_id_by_start_date(db, start_date=start_date, owner_id=owner_id)
    if db_conferences is None or len(db_conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

# get all conferences by owner_id by end_date
@router.get("/conferences/owner/{owner_id}/end_date/{end_date}", response_model=list[schemas.Conference])
def get_all_conferences_owner_id_by_end_date(owner_id: int, end_date: date, db: Session = Depends(get_db)):
    if owner_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid owner id")
    if users_crud.get_user(db, user_id=owner_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_conferences = crud.get_conferences_owner_id_by_end_date(db, end_date=end_date, owner_id=owner_id)
    if db_conferences is None or len(db_conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

# get all conferences by owner_id by description
@router.get("/conferences/owner/{owner_id}/description/{description}", response_model=list[schemas.Conference])
def get_all_conferences_owner_id_by_description(owner_id: int, description: str, db: Session = Depends(get_db)):
    if description.isnumeric() or owner_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference name or owner id")
    if users_crud.get_user(db, user_id=owner_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_conferences = crud.get_conferences_owner_id_by_description(db, description=description, owner_id=owner_id)
    if db_conferences is None or len(db_conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

# get all conferences by owner_id
@router.get("/conferences/owner/{owner_id}", response_model=list[schemas.Conference])
def get_all_conferences_by_owner_id(owner_id: int, db: Session = Depends(get_db)):
    if owner_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid owner id")
    if users_crud.get_user(db, user_id=owner_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_conferences = crud.get_conferences_by_owner_id(db, owner_id=owner_id)
    if db_conferences is None or len(db_conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

# get all conferences by owner_id and conference id and between start_date and end_date
@router.get("/conferences/owner_id/{owner_id}/start_date/{filter_start_date}/end_date/{filter_end_date}", response_model=list[schemas.Conference])
def get_all_conferences_by_owner_id_between_start_date_and_end_date(owner_id: int, filter_start_date: date, filter_end_date: date, db: Session = Depends(get_db)):
    if owner_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id")
    if users_crud.get_user(db, user_id=owner_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    if filter_start_date > filter_end_date:
        raise HTTPException(status_code=400, detail="Invalid date range")
    db_conferences = crud.get_conferences_by_owner_id_between_start_date_and_end_date(db, owner_id=owner_id, filter_start_date=filter_start_date, filter_end_date=filter_end_date)
    if db_conferences is None or len(db_conferences) == 0:
        raise HTTPException(status_code=404, detail="Conference not found")
    return db_conferences

# update conference by conference id
@router.put("/conferences/{conference_id}", response_model=schemas.Conference)
def update_conference(conference_id: int, conference: schemas.ConferenceCreate, db: Session = Depends(get_db)):
    if conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid conference id")
    db_conference = crud.get_conference(db, conference_id=conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    if conference.start_date > conference.end_date:
        raise HTTPException(status_code=400, detail="Invalid date range")
    return crud.update_user_conference(db=db, conference=conference, conference_id=conference_id)

# update conference by owner id and conference id
@router.put("/conferences/owner_id/{owner_id}/conference/{conference_id}", response_model=schemas.Conference)
def update_conference(owner_id: int, conference_id: int, conference: schemas.ConferenceCreate, db: Session = Depends(get_db)):
    if owner_id <= 0 or conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id or conference id")
    if not users_crud.get_user(db, user_id=owner_id):
        raise HTTPException(status_code=404, detail="User not found")
    db_conference = crud.get_conference_by_owner_id(db, owner_id=owner_id, conference_id=conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    if conference.start_date > conference.end_date:
        raise HTTPException(status_code=400, detail="Invalid date range")
    return crud.update_conference(db=db, owner_id=owner_id, conference=conference, conference_id=conference_id)

# delete conference
@router.delete("/conferences/owner_id/{owner_id}/conference/{conference_id}")
def delete_conference_owner_id_conference_id(owner_id: int, conference_id: int, db: Session = Depends(get_db)):
    if owner_id <= 0 or conference_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id or conference id")
    if not users_crud.get_user(db, user_id=owner_id):
        raise HTTPException(status_code=404, detail="User not found")
    db_conference = crud.get_conference_by_owner_id(db,owner_id=owner_id, conference_id=conference_id)
    if db_conference is None:
        raise HTTPException(status_code=404, detail="Conference not found")
    return crud.delete_conference(db=db, owner_id=owner_id, conference_id=conference_id)

# delete all conferences by owner id
@router.delete("/conferences/owner/{owner_id}")
def delete_all_conferences_by_owner_id(owner_id: int, db: Session = Depends(get_db)):
    if owner_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid owner id")
    if not users_crud.get_user(db, user_id=owner_id):
        raise HTTPException(status_code=404, detail="User not found")
    db_conferences = crud.get_conferences_by_owner_id(db, owner_id=owner_id)
    if db_conferences is None or len(db_conferences) == 0:
        raise HTTPException(status_code=404, detail="No conferences found for owner")
    return crud.delete_all_conferences_of_owner_id(db=db, owner_id=owner_id)