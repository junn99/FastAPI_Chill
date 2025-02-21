from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/brands", tags=["brands"])

# 브랜드 스키마 정의
class BrandBase(BaseModel):
    # code: str
    brand_name: str
    capital: int = None
    min_price: int
    max_price: int
    price: int
    moq: int
    planned_launch: str = None 
    represetative_info: str = None
    history: str = None
    performance: str = None
    marketing_plan: str = None
    business_plan: str = None
    

class BrandCreate(BrandBase):
    pass

class Brand(BrandBase):
    id: int
    created_at: datetime
    
    class Config:
        orm_mode = True

# 브랜드 목록 조회
@router.get("/", response_model=List[Brand])
def get_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    brands = db.query(models.Brand).offset(skip).limit(limit).all()
    return brands

# 브랜드 상세 조회
@router.get("/{brand_id}", response_model=Brand)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

# 브랜드 이름으로 조회
@router.get("/by-name/{name}", response_model=Brand)
def get_brand_by_name(name: str, db: Session = Depends(get_db)):
    brand = db.query(models.Brand).filter(models.Brand.brand_name == name).first()
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand

# 브랜드 생성
@router.post("/", response_model=Brand)
def create_brand(brand: BrandCreate, db: Session = Depends(get_db)):
    db_brand = db.query(models.Brand).filter(models.Brand.brand_name == brand.brand_name).first()
    if db_brand:
        raise HTTPException(status_code=400, detail="Brand name already registered")
    new_brand = models.Brand(**brand.model_dump())
    db.add(new_brand)
    db.commit()
    db.refresh(new_brand)
    return new_brand

# 브랜드 정보 업데이트
@router.put("/{brand_id}", response_model=Brand)
def update_brand(brand_id: int, brand: BrandBase, db: Session = Depends(get_db)):
    db_brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()
    if db_brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    for key, value in brand.model_dump().items():
        setattr(db_brand, key, value)
    
    db.commit()
    db.refresh(db_brand)
    return db_brand

# 브랜드 삭제
@router.delete("/{brand_id}", response_model=Brand)
def delete_brand(brand_id: int, db: Session = Depends(get_db)):
    db_brand = db.query(models.Brand).filter(models.Brand.id == brand_id).first()
    if db_brand is None:
        raise HTTPException(status_code=404, detail="Brand not found")
    
    db.delete(db_brand)
    db.commit()
    return db_brand