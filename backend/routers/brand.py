from fastapi import APIRouter
from .schemas import BrandBase, BrandCreate, BrandRead
# from ..database import get_db
from .crud import create_brand
from models import Brand

## 종속성 주입
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends

# db_dependency = Annotated[Session, Depends(get_db)]

router = APIRouter(
    prefix="/brand",
    tags=["brand"]
)

# @router.post("/")
# async def create_new_brand(db: db_dependency,
#                            brand: BrandCreate):
#     brand_data = Brand(**brand.model_dump())
#     created_brand = create_brand(db_dependency, brand_data)
#     return created_brand

# @router.post("/")
# def create_new_brand(brand_data: BrandCreate, db: Session = Depends(get_db)):
#     created_brand = create_brand(db, brand_data)  # ✅ 세션 객체 전달
#     return created_brand
    # sqlalchemy.orm.exc.UnmappedInstanceError: Class 'routers.schemas.BrandCreate' is not mapped
    # QLAlchemy의 session.add()에 Pydantic 모델(BrandCreate)을 전달했기 때문에 발생
    # BrandCreate는 SQLAlchemy의 ORM 모델이 아니라 Pydantic 스키마이기 때문에, DB에 바로 추가할 수 없음

# from models import Brand  # SQLAlchemy ORM 모델 가져오기
# @router.post("/")
# # def create_brand(brand_data: BrandCreate, db: Session = Depends(get_db)):
# def create_brand(db: db_dependency, brand_data: BrandCreate):
#     # 무조권 db_dependency 이렇게 써야겟네, 아니면 위에 처럼 순서에 신경써야 해서 머리아픔
#     # ✅ Pydantic 모델을 SQLAlchemy ORM 객체로 변환
#     new_brand = Brand(
#         brand_name=brand_data.brand_name,
#         capital=brand_data.capital,
#         min_price=brand_data.min_price,
#         max_price=brand_data.max_price,
#         price=brand_data.price,
#         moq=brand_data.moq,
#         planned_launch=brand_data.planned_launch,
#         represetative_info=brand_data.represetative_info,
#         history=brand_data.history,
#         performance=brand_data.performance,
#         marketing_plan=brand_data.marketing_plan,
#         business_plan=brand_data.business_plan
#     )

#     db.add(new_brand)  # ✅ ORM 객체를 추가
#     db.commit()
#     db.refresh(new_brand)  # ✅ 최신 데이터 반영
#     return new_brand


# @router.post("/2")
# async def async_create_brand(db: db_dependency, brand: BrandCreate):
#     brand = Brand(**brand.model_dump())
#     created_brand = await create_brand(db, brand)
#     return created_brand



from database import async_get_db
from sqlalchemy.ext.asyncio import AsyncSession


@router.post("/create")
async def create_new_brand(brand: BrandCreate, db: AsyncSession = Depends(async_get_db)):
    brand = Brand(**brand.model_dump())
    created_brand = await create_brand(brand, db)
    return created_brand


from routers.crud import get_brands
from typing import List

@router.get("/read", response_model=List[BrandRead])
# BrandRead or BrandBase = 내보낼 내용
async def read_brands(
    db: AsyncSession = Depends(async_get_db),
):
    brands = await get_brands(db)
    return brands