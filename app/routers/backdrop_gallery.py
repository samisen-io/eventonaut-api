import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from app.crud import backdrop_gallery_crud as crud
from app.oauth2 import get_current_active_user
from app.schemas import backdrop_gallery_schemas as schemas
from app.dependencies import get_db

router = APIRouter(tags=["backdrop"])

def get_backdrop_by_id(backdrop_id: str, db: Session, User):
    db_backdrop = crud.get_backdrop_by_id(db, backdrop_id=backdrop_id, owner_id=User.id)
    if db_backdrop is None:
        raise HTTPException(status_code=404, detail="Backdrop not found")
    return db_backdrop

@router.get("/backdrop/{backdrop_id}", response_model=schemas.BackdropGalleryResponse)
def Get_backdrop(backdrop_id: str, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=["organizer", "attendee"])):
    db_backdrop = get_backdrop_by_id(backdrop_id, db, User)
    return schemas.BackdropGalleryResponse(conference_id=db_backdrop.conference.uuid, 
                                           backdrop_url=db_backdrop.backdrop_url, 
                                           uuid=db_backdrop.uuid)

@router.get("/backdrops/{conference_id}", response_model=List[schemas.BackdropGalleryResponse])
def get_backdrops_by_conferene_id(conference_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=["organizer", "attendee"])):
    try:
        backdrops = crud.get_backdrops_by_conference_id(db, conference_id=conference_id, owner_id=User.id, skip=skip, limit=limit)
        response = [schemas.BackdropGalleryResponse(conference_id=conference_id, 
                                                    backdrop_url=backdrop.backdrop_url, 
                                                    uuid=backdrop.uuid) for backdrop in backdrops]
        return response
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/backdrop", response_model=schemas.BackdropGalleryResponse)
def create_backdrop(backdrop: schemas.BackdropGalleryCreate, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=["organizer"])):
    try:
        modelresponse = crud.create_backdrop(db=db, backdrop=backdrop, owner_id=User.id)
        response = schemas.BackdropGalleryResponse(conference_id=backdrop.conference_id, 
                                                backdrop_url=modelresponse.backdrop_url, 
                                                uuid=modelresponse.uuid)
        return response
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/backdrop/{backdrop_id}", response_model=schemas.BackdropGalleryUpdateResponse)
def update_backdrop(backdrop: schemas.BackdropGalleryUpdate, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=["organizer"])):
    db_backdrop = get_backdrop_by_id(backdrop.id, db, User)
    updated_backdrop = crud.update_backdrop(db=db, backdrop=backdrop, db_backdrop=db_backdrop)
    response = schemas.BackdropGalleryUpdateResponse(backdrop_url=updated_backdrop.backdrop_url, 
                                                    uuid=updated_backdrop.uuid)
    return response

@router.delete("/backdrop/{backdrop_id}")
def delete_backdrop(backdrop_id: str, db: Session = Depends(get_db),  User = Security(get_current_active_user, scopes=["organizer"])):
    db_backdrop = get_backdrop_by_id(backdrop_id, db, User)
    crud.delete_backdrop(db=db, db_backdrop=db_backdrop)
    return {"detail": "Backdrop deleted"}
