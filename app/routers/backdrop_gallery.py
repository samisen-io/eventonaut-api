import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.orm import Session
from app.crud import backdrop_gallery_crud as crud, conferences_crud as conf_crud
from app.oauth2 import get_current_active_organization, get_current_active_user
from app.schemas import backdrop_gallery_schemas as schemas, organization_schemas
from app.dependencies import get_db
from app.static_enums.role import RoleEnum
from app.schemas.user_schemas import UserAuthentication as User

router = APIRouter(tags=["backdrop"])

def get_backdrop_by_id(backdrop_id: str, db: Session, organization):
    db_backdrop = crud.get_backdrop_by_id(db, backdrop_id=backdrop_id, organization_id=organization.id)
    if db_backdrop is None:
        raise HTTPException(status_code=404, detail="Backdrop not found")
    return db_backdrop

@router.get("/backdrops", response_model=List[schemas.BackdropGalleryResponse])
def get_all_backdrops_by_organization_id(offset: int = 0, limit: int = 100, db: Session = Depends(get_db), current_organization: organization_schemas.OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name])):
    try:
        backdrops = crud.get_all_backdrops_by_organization_id(db=db, organization_id=current_organization.id, offset=offset, limit=limit)
        response = [schemas.BackdropGalleryResponse(conference_id=backdrop.conference.uuid, 
                                                    backdrop_url=backdrop.backdrop_url, 
                                                    name=backdrop.name,
                                                    size=backdrop.size,
                                                    uuid=backdrop.uuid) for backdrop in backdrops]
        return response
    except HTTPException as e:
        logging.exception(str(e))
        raise e
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/backdrop/{backdrop_id}", response_model=schemas.BackdropGalleryResponse)
def Get_backdrop(backdrop_id: str, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, RoleEnum.ATTENDEE.name, "organizer", "attendee"])):
    roles = [user_role.role for user_role in current_user.user_roles]
    if roles[0].name == RoleEnum.ATTENDEE.name:
        db_backdrop = crud.get_backdrop(db, backdrop_id)
    elif roles[0].name == RoleEnum.ORGANIZATION_ADMIN.name or roles[0].name == RoleEnum.ORGANIZATION_USER.name:
        organization_id = current_user.organization_user[0].organization_id
        db_backdrop = crud.get_backdrop_by_id(db, backdrop_id, organization_id)
    return schemas.BackdropGalleryResponse(conference_id=db_backdrop.conference.uuid, 
                                           backdrop_url=db_backdrop.backdrop_url, 
                                           name=db_backdrop.name,
                                           size=db_backdrop.size,
                                           uuid=db_backdrop.uuid)

@router.get("/backdrops/{conference_id}", response_model=List[schemas.BackdropGalleryResponse])
def get_backdrops_by_conferene_id(conference_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Security(get_current_active_user, scopes=[RoleEnum.ORGANIZATION_ADMIN.name, RoleEnum.ORGANIZATION_USER.name, RoleEnum.ATTENDEE.name,"organizer", "attendee"])):
    try:
        conference = conf_crud.get_conference(db, conference_id)
        if not conference:
            logging.exception(f"Conference not found")
            raise HTTPException(status_code=404, detail="Conference not found")
        roles = [user_role.role for user_role in current_user.user_roles]
        if roles[0].name == RoleEnum.ATTENDEE.name:
            backdrops = crud.get_backdrops_by_conference(db, conference_id=conference.id, skip=skip, limit=limit)
        elif roles[0].name == RoleEnum.ORGANIZATION_ADMIN.name or roles[0].name == RoleEnum.ORGANIZATION_USER.name:
            organization_id = current_user.organization_user[0].organization_id
            backdrops = crud.get_backdrops_by_conference_id(db, conference_id=conference.id, organization_id=organization_id, skip=skip, limit=limit)
        response = [schemas.BackdropGalleryResponse(conference_id=conference_id, 
                                                    backdrop_url=backdrop.backdrop_url, 
                                                    name=backdrop.name,
                                                    size=backdrop.size,
                                                    uuid=backdrop.uuid) for backdrop in backdrops]
        return response
    except HTTPException as e:
        logging.exception(str(e))
        raise e
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/backdrop", response_model=schemas.BackdropGalleryResponse)
def create_backdrop(backdrop: schemas.BackdropGalleryCreate, db: Session = Depends(get_db), current_organization: organization_schemas.OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name, "organizer"])):
    try:
        modelresponse = crud.create_backdrop(db=db, backdrop=backdrop, organization_id=current_organization.id)
        response = schemas.BackdropGalleryResponse(conference_id=backdrop.conference_id, 
                                                backdrop_url=modelresponse.backdrop_url,
                                                name=modelresponse.name,
                                                size=modelresponse.size,
                                                uuid=modelresponse.uuid)
        return response
    except HTTPException as e:
        print("printing",e.detail)
        raise
    except Exception as e:
        logging.exception(str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.put("/backdrop/{backdrop_id}", response_model=schemas.BackdropGalleryUpdateResponse)
def update_backdrop(backdrop: schemas.BackdropGalleryUpdate, db: Session = Depends(get_db), current_organization: organization_schemas.OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name, "organizer"])):
    db_backdrop = get_backdrop_by_id(backdrop.id, db, current_organization)
    updated_backdrop = crud.update_backdrop(db=db, backdrop=backdrop, db_backdrop=db_backdrop)
    response = schemas.BackdropGalleryUpdateResponse(backdrop_url=updated_backdrop.backdrop_url, 
                                                     name=updated_backdrop.name,
                                                     size=updated_backdrop.size,
                                                    uuid=updated_backdrop.uuid)
    return response

@router.delete("/backdrop/{backdrop_id}")
def delete_backdrop(backdrop_id: str, db: Session = Depends(get_db),  current_organization: organization_schemas.OrganizationSecurity = Security(get_current_active_organization, scopes=[RoleEnum.ORGANIZATION_USER.name, RoleEnum.ORGANIZATION_ADMIN.name, "organizer"])):
    db_backdrop = get_backdrop_by_id(backdrop_id, db, current_organization)
    crud.delete_backdrop(db=db, db_backdrop=db_backdrop)
    return {"detail": "Backdrop deleted"} 