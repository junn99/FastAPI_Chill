from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
import models
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/manufacturers", tags=["manufacturers"])

# 제조사 스키마 정의
class ManufacturerBase(BaseModel):
    name: str
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[str] = None
    specialties: Optional[str] = None

class ManufacturerCreate(ManufacturerBase):
    pass

class Manufacturer(ManufacturerBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# 프로젝트-제조사 연결 스키마
class ProjectManufacturerBase(BaseModel):
    project_id: int
    manufacturer_id: int
    status: str = None
    notes: str = None

class ProjectManufacturerCreate(ProjectManufacturerBase):
    pass

class ProjectManufacturer(ProjectManufacturerBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# 제조사 목록 조회
@router.get("/", response_model=List[Manufacturer])
def get_manufacturers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    manufacturers = db.query(models.Manufacturer).offset(skip).limit(limit).all()
    return manufacturers

# 제조사 상세 조회
@router.get("/{manufacturer_id}", response_model=Manufacturer)
def get_manufacturer(manufacturer_id: int, db: Session = Depends(get_db)):
    manufacturer = db.query(models.Manufacturer).filter(models.Manufacturer.id == manufacturer_id).first()
    if manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    return manufacturer

# 제조사 이름으로 조회
@router.get("/by-name/{name}", response_model=Manufacturer)
def get_manufacturer_by_name(name: str, db: Session = Depends(get_db)):
    manufacturer = db.query(models.Manufacturer).filter(models.Manufacturer.name == name).first()
    if manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    return manufacturer

# 제조사 생성
@router.post("/", response_model=Manufacturer)
def create_manufacturer(manufacturer: ManufacturerCreate, db: Session = Depends(get_db)):
    db_manufacturer = db.query(models.Manufacturer).filter(models.Manufacturer.name == manufacturer.name).first()
    if db_manufacturer:
        raise HTTPException(status_code=400, detail="Manufacturer name already registered")
    new_manufacturer = models.Manufacturer(**manufacturer.dict())
    db.add(new_manufacturer)
    db.commit()
    db.refresh(new_manufacturer)
    return new_manufacturer

# 제조사 정보 업데이트
@router.put("/{manufacturer_id}", response_model=Manufacturer)
def update_manufacturer(manufacturer_id: int, manufacturer: ManufacturerBase, db: Session = Depends(get_db)):
    db_manufacturer = db.query(models.Manufacturer).filter(models.Manufacturer.id == manufacturer_id).first()
    if db_manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    
    for key, value in manufacturer.dict().items():
        setattr(db_manufacturer, key, value)
    
    db.commit()
    db.refresh(db_manufacturer)
    return db_manufacturer

# 제조사 삭제
@router.delete("/{manufacturer_id}", response_model=Manufacturer)
def delete_manufacturer(manufacturer_id: int, db: Session = Depends(get_db)):
    db_manufacturer = db.query(models.Manufacturer).filter(models.Manufacturer.id == manufacturer_id).first()
    if db_manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    
    db.delete(db_manufacturer)
    db.commit()
    return db_manufacturer

# 제조사의 프로젝트 목록 조회
@router.get("/{manufacturer_id}/projects", response_model=List[ProjectManufacturer])
def get_manufacturer_projects(manufacturer_id: int, db: Session = Depends(get_db)):
    manufacturer = db.query(models.Manufacturer).filter(models.Manufacturer.id == manufacturer_id).first()
    if manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    
    projects = db.query(models.ProjectManufacturer).filter(
        models.ProjectManufacturer.manufacturer_id == manufacturer_id
    ).all()
    
    return projects

# 프로젝트-제조사 연결 생성 (프로젝트 참여)
@router.post("/project-connections", response_model=ProjectManufacturer)
def create_project_connection(connection: ProjectManufacturerCreate, db: Session = Depends(get_db)):
    # 프로젝트 존재 확인
    project = db.query(models.Project).filter(models.Project.id == connection.project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # 제조사 존재 확인
    manufacturer = db.query(models.Manufacturer).filter(models.Manufacturer.id == connection.manufacturer_id).first()
    if manufacturer is None:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    
    # 이미 연결되어 있는지 확인
    existing = db.query(models.ProjectManufacturer).filter(
        models.ProjectManufacturer.project_id == connection.project_id,
        models.ProjectManufacturer.manufacturer_id == connection.manufacturer_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Connection already exists")
    
    new_connection = models.ProjectManufacturer(**connection.dict())
    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)
    return new_connection

# 프로젝트-제조사 연결 상태 업데이트
@router.put("/project-connections/{connection_id}", response_model=ProjectManufacturer)
def update_project_connection(
    connection_id: int, 
    status: str = None, 
    notes: str = None, 
    db: Session = Depends(get_db)
):
    db_connection = db.query(models.ProjectManufacturer).filter(models.ProjectManufacturer.id == connection_id).first()
    if db_connection is None:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    if status is not None:
        db_connection.status = status
    
    if notes is not None:
        db_connection.notes = notes
    
    db.commit()
    db.refresh(db_connection)
    return db_connection

# 프로젝트-제조사 연결 삭제
@router.delete("/project-connections/{connection_id}", response_model=ProjectManufacturer)
def delete_project_connection(connection_id: int, db: Session = Depends(get_db)):
    db_connection = db.query(models.ProjectManufacturer).filter(models.ProjectManufacturer.id == connection_id).first()
    if db_connection is None:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    db.delete(db_connection)
    db.commit()
    return db_connection