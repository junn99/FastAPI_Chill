# from fastapi import FastAPI
# import models
# from database import engine
# from routers import brand

# models.Base.metadata.create_all(bind=engine)

# app = FastAPI(title="Brand API")

# # 라우터 등록
# app.include_router(brand.router)


# @app.get("/")
# def read_root():
#     return {"message": "Welcome to Brand Manager API"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)




# ============================================================
# 비동기 적용
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from database import init_db, async_get_db

from models import Brand
from routers.schemas import BrandCreate
from routers.crud import create_brand


@asynccontextmanager
    # 리소스 초기화 및 정리(cleanup) 작업을 위해 사용
    # 비동기 초기화 & 종료 처리를 함수 내부에서 관리
    # 앱 실행과 종료 시 필요한 작업을 쉽게 관리
async def startup_event(app: FastAPI):
    await init_db()
    try:
        yield
    finally:
        pass

app = FastAPI(lifespan=startup_event)




# 미들웨어(streamlit) 연결
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 라우트 연결
from routers import brand

app.include_router(brand.router)