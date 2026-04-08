from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

import models
import schemas
import services
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Travel Planner API")

@app.post("/projects/", response_model=schemas.ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project_data: schemas.ProjectCreate, db: Session = Depends(get_db)):
    new_project = models.Project(
        name=project_data.name,
        description=project_data.description,
        start_date=project_data.start_date
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    if project_data.places:
        if len(project_data.places) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 places per project")
        for p in project_data.places:
            is_valid = await services.validate_artwork_id(p.external_api_id)
            if not is_valid:
                raise HTTPException(status_code=400, detail=f"Place ID {p.external_api_id} not found in Art Institute API")
            
            new_place = models.ProjectPlace(
                project_id=new_project.id,
                external_api_id=p.external_api_id,
                notes=p.notes
            )
            db.add(new_place)
        
        db.commit()
        db.refresh(new_project)
        
    return new_project

@app.get("/projects/", response_model=List[schemas.ProjectResponse])
def list_projects(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.Project).offset(skip).limit(limit).all()

@app.get("/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if any(place.is_visited for place in project.places):
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete project if any places are marked as visited"
        )
    
    db.delete(project)
    db.commit()
    return None


@app.post("/projects/{project_id}/places/", response_model=schemas.ProjectPlaceResponse)
async def add_place_to_project(
    project_id: int, 
    place_data: schemas.ProjectPlaceCreate, 
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if len(project.places) >= 10:
        raise HTTPException(status_code=400, detail="Project already has 10 places")

    existing = db.query(models.ProjectPlace).filter(
        models.ProjectPlace.project_id == project_id,
        models.ProjectPlace.external_api_id == place_data.external_api_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="This place is already in the project")

    if not await services.validate_artwork_id(place_data.external_api_id):
        raise HTTPException(status_code=400, detail="Invalid External API ID")

    new_place = models.ProjectPlace(**place_data.model_dump(), project_id=project_id)
    db.add(new_place)
    
    project.is_completed = False
    
    db.commit()
    db.refresh(new_place)
    return new_place

@app.patch("/projects/places/{place_id}", response_model=schemas.ProjectPlaceResponse)
def update_place(place_id: int, update_data: schemas.ProjectPlaceUpdate, db: Session = Depends(get_db)):
    place = db.query(models.ProjectPlace).filter(models.ProjectPlace.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")

    if update_data.notes is not None:
        place.notes = update_data.notes
    
    if update_data.is_visited is not None:
        place.is_visited = update_data.is_visited
        db.commit()
        
        project = place.project
        all_visited = all(p.is_visited for p in project.places)
        if all_visited:
            project.is_completed = True
        else:
            project.is_completed = False
        db.commit()

    db.refresh(place)
    return place