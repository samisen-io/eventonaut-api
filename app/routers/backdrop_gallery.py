from typing import List
from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from app.crud import backdrop_gallery_crud as crud
from app.oauth2 import get_current_active_user
from app.schemas import backdrop_gallery_schemas as schemas
from app.dependencies import get_db

router = APIRouter()

@router.get("/{backdrop_id}", response_model=schemas.BackdropGalleryResponse)
def read_backdrop(backdrop_id: str, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=["organizer"])):
    db_backdrop = crud.get_backdrop_by_id(db, backdrop_id=backdrop_id, owner_id=User.id)
    if db_backdrop is None:
        raise HTTPException(status_code=404, detail="Backdrop not found")
    return db_backdrop

@router.get("/", response_model=List[schemas.BackdropGalleryResponse])
def read_backdrops(conference_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), User = Security(get_current_active_user, scopes=["organizer"])):
    backdrops = crud.get_backdrops_by_conference_id(db, conference_id=conference_id, owner_id=User.id, skip=skip, limit=limit)
    return backdrops

@router.post("/", response_model=schemas.BackdropGalleryResponse)
def create_backdrop(backdrop: schemas.BackdropGalleryCreate, owner_id: int, db: Session = Depends(get_db)):
    return crud.create_backdrop(db=db, backdrop=backdrop, owner_id=owner_id)

@router.put("/{backdrop_id}", response_model=schemas.BackdropGalleryResponse)
def update_backdrop(backdrop_id: str, backdrop: schemas.BackdropGalleryCreate, db: Session = Depends(get_db)):
    db_backdrop = crud.get_backdrop_by_id(db, backdrop_id=backdrop_id)
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