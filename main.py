from typing import List

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

import database
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