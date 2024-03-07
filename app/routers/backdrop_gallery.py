import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from app.crud import backdrop_gallery_crud as crud
from app.oauth2 import get_current_active_user
from app.schemas import backdrop_gallery_schemas as schemas
from app.dependencies import get_db

router = APIRouter(tags=["backdrop"])

# @router.get("/{backdrop_id}", response_model=schemas.BackdropGalleryResponse)
# def Get_backdrop(backdrop_id: str, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=["organizer"])):
#     db_backdrop = crud.get_backdrop_by_id(db, backdrop_id=backdrop_id, owner_id=User.id)
#     if db_backdrop is None:
#         raise HTTPException(status_code=404, detail="Backdrop not found")
#     return schemas.BackdropGalleryResponse(conference_id=db_backdrop.conference.uuid, 
#                                                 backdrop_url=db_backdrop.backdrop_url, 
#                                                 uuid=db_backdrop.uuid)

@router.get("/all_backdrops", response_model=List[schemas.BackdropGalleryResponse])
def get_backdrops_by_conferene_id(conference_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=["organizer"])):
    try:
        backdrops = crud.get_backdrops_by_conference_id(db, conference_id=conference_id, owner_id=21, skip=skip, limit=limit)
        response = [schemas.BackdropGalleryResponse(conference_id=conference_id, 
                                                    backdrop_url=backdrop.backdrop_url, 
                                                    uuid=backdrop.uuid) for backdrop in backdrops]
        return response
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/", response_model=schemas.BackdropGalleryResponse)
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
    
@router.put("/{backdrop_id}", response_model=schemas.BackdropGalleryResponse)
def update_backdrop(backdrop: schemas.BackdropGalleryUpdate, db: Session = Depends(get_db)):
    db_backdrop = crud.get_backdrop_by_id(db, backdrop_id=backdrop.uuid, owner_id=21)
    if db_backdrop is None:
        raise HTTPException(status_code=404, detail="Backdrop not found")
    return crud.update_backdrop(db=db, backdrop=backdrop, db_backdrop=db_backdrop)

@router.delete("/{backdrop_id}")
def delete_backdrop(backdrop_id: str, db: Session = Depends(get_db)):
    db_backdrop = crud.get_backdrop_by_id(db, backdrop_id=backdrop_id)
    if db_backdrop is None:
        raise HTTPException(status_code=404, detail="Backdrop not found")
    crud.delete_backdrop(db=db, db_backdrop=db_backdrop)
    return {"detail": "Backdrop deleted"}