# from sqlalchemy.future import select
# from sqlalchemy import update, delete

# from models import Brand
# from .schemas import BrandCreate


# ## 종속성 주입
# from database import get_db
# from typing import Annotated
# from sqlalchemy.orm import Session
# from fastapi import Depends

# db_dependency = Annotated[Session, Depends(get_db)]

# Brand - crud

# def create_brand(db: db_dependency, brand: BrandCreate):
#     db.add(brand)
#         # db넣을 땐, 정의한 모델과 일치해야 함
#         # 아니라면 하나하나 다 정의해줘야 함
#     db.commit()
#     db.refresh(brand)

#     return brand





# ================================
# 비동기 적용!
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from models import Brand


async def create_brand(brand: Brand, db: AsyncSession):
    db.add(brand)
    await db.commit()
    await db.refresh(brand)
    return brand


from sqlalchemy.future import select
    # 비동기 명령어

async def get_brands(db: AsyncSession):
    # No query in async
    stmt = select(Brand)
    results = await db.execute(stmt)
    return results.scalars().all()
