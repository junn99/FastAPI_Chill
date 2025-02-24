from pydantic import BaseModel
from typing import Optional
# from datetime import  data, datetime


# 브랜드 스키마 정의 : 받아야 할 정보? 정도로 보면 되지 않을까
# models.py에서 정의한 테이블 참고해야 함 ㅇㅇ
# API 요청/응답의 데이터 유효성을 검증
class BrandBase(BaseModel):
    # code: str
    brand_name: str
    capital: Optional[int] = None
    min_price: int
    max_price: int
    price: int
    moq: int
    planned_launch: Optional[str] = None

    # ==== 프로젝트 ====
    represetative_info: Optional[str] = None
    history: Optional[str] = None
    performance: Optional[str] = None
    marketing_plan: Optional[str] = None
    business_plan: Optional[str] = None


class BrandCreate(BrandBase):
    pass

class BrandRead(BaseModel):
    brand_name: str
    price: int
    moq: int