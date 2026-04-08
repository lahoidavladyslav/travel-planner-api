from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False)

    places = relationship("ProjectPlace", back_populates="project", cascade="all, delete-orphan")


class ProjectPlace(Base):
    __tablename__ = "project_places"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    external_api_id = Column(Integer, nullable=False)
    notes = Column(String, nullable=True)
    is_visited = Column(Boolean, default=False)

    project = relationship("Project", back_populates="places")