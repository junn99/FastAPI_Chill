from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, Identity
from sqlalchemy.orm import relationship
from database import Base

class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(Integer, Identity(start=1, increment=1) ,primary_key=True)
    # 브랜드 코드 : 링크 생성
    # code = Column(String, nullable=False, unique=True)
    
    brand_name = Column(String, index=True, nullable=False)
    # 자본금
    capital = Column(Integer, nullable=True)
    # 최소/최대 단가 허용치
    min_price = Column(Integer, nullable=False)
    max_price = Column(Integer, nullable=False)
    # 목표 단가
    price = Column(Integer, nullable=False)
    moq = Column(Integer, nullable=False)
    # 납품 기한
    planned_launch = Column(String, nullable=True)

    # ================ 프로젝트로 따로 분리마려움 ============
    
    # 대표자 정보
    represetative_info = Column(String, nullable=True)
    # 회사 연혁
    history = Column(String, nullable=True)
    # 회사 실적
    performance = Column(String, nullable=True)
    # 마케팅 계획
    marketing_plan = Column(String, nullable=True)
    # 사업 계획
    business_plan = Column(String, nullable=True)

    created_at = Column(DateTime, default=func.now())
    # updated_at = Column(DateTime, nullable=True)
    
    projects = relationship("Project", back_populates="brand")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"))
    name = Column(String)
    description = Column(Text, nullable=True)
    start_date = Column(String)
    end_date = Column(String)
    status = Column(String)
    requirements = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    brand = relationship("Brand", back_populates="projects")
    manufacturers = relationship("ProjectManufacturer", back_populates="project")

class Manufacturer(Base):
    __tablename__ = "manufacturers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    contact_person = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    capacity = Column(String, nullable=True)
    specialties = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    projects = relationship("ProjectManufacturer", back_populates="manufacturer")

class ProjectManufacturer(Base):
    __tablename__ = "project_manufacturers"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"))
    status = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    project = relationship("Project", back_populates="manufacturers")
    manufacturer = relationship("Manufacturer", back_populates="projects")