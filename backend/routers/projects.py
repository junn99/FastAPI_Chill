from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/projects", tags=["projects"])

# 프로젝트 스키마 정의
class ProjectBase(BaseModel):
    brand_id: int
    name: str
    description: str = None
    start_date: str
    end_date: str
    status: str
    requirements: str = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# 프로젝트 목록 조회
@router.get("/", response_model=List[Project])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    return projects

# 특정 브랜드의 프로젝트 목록 조회
@router.get("/brand/{brand_id}", response_model=List[Project])
def get_brand_projects(brand_id: int, db: Session = Depends(get_db)):
    projects = db.query(models.Project).filter(models.Project.brand_id == brand_id).all()
    return projects

# 프로젝트 상세 조회
@router.get("/{project_id}", response_model=Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

# 프로젝트 생성
@router.post("/", response_model=Project)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    # 브랜드 존재 확인
    brand = db.query(models.Brand).filter(models.Brand.id == project.brand_id).first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
        
    new_project = models.Project(**project.dict())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

# 프로젝트 정보 업데이트
@router.put("/{project_id}", response_model=Project)
def update_project(project_id: int, project: ProjectBase, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 브랜드 존재 확인
    brand = db.query(models.Brand).filter(models.Brand.id == project.brand_id).first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    for key, value in project.dict().items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

# 프로젝트 삭제
@router.delete("/{project_id}", response_model=Project)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return db_project

# 프로젝트 상태 변경
@router.patch("/{project_id}/status", response_model=Project)
def update_project_status(project_id: int, status: str, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db_project.status = status
    db.commit()
    db.refresh(db_project)
    return db_project