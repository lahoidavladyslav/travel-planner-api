from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class ProjectPlaceBase(BaseModel):
    external_api_id: int
    notes: Optional[str] = None

class ProjectPlaceCreate(ProjectPlaceBase):
    pass

class ProjectPlaceUpdate(BaseModel):
    notes: Optional[str] = None
    is_visited: Optional[bool] = None

class ProjectPlaceResponse(ProjectPlaceBase):
    id: int
    is_visited: bool
    
    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None

class ProjectCreate(ProjectBase):
    places: Optional[List[ProjectPlaceCreate]] = []

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[date] = None

class ProjectResponse(ProjectBase):
    id: int
    is_completed: bool
    places: List[ProjectPlaceResponse]

    class Config:
        from_attributes = True