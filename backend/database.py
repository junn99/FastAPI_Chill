# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base

# # 1. FastAPI application이 데이터베이스 위치를 만드는 데 사용
# # 데이터베이스 URL 설정: SQLite 사용할 경우
# SQLALCHEMY_DATABASE_URL = "sqlite:///./DealMakers.db"


# # 2. application을 위한 엔진 설정 : 데이터베이스 사용
# # 데이터베이스 엔진 생성 : DB URL받아서 연결 pool 생성
# engine = create_engine(
# 	SQLALCHEMY_DATABASE_URL,	
# 	connect_args={'check_same_thread': False} # SQLite용 설정 값
# 		# SQLite에서 여러 요청을 동시에 처리하기 위한 설정
# )

# # 3. 세션 로컬 생성
# # 세션 로컬의 인스턴스마다 데이터베이스 세션을 가짐
# # 세션팩토리 설정 : 각 API 요청마다 독립적인 DB 세션 생성
# SessionLocal = sessionmaker(
# 	autocommit=False, # 자동 커밋 비활성화
# 	autoflush=False,  # 자동 플러시 비활성화
# 	bind=engine       # 위에서 생성한 엔진과 연결
# )


# # 4. 데이터베이스 객체 만들기
# # 모델 생성을 위한 Base 클래스
# 	# Base를 상속받아 데이터베이스 테이블 정의(생성)
# Base = declarative_base()
# 	# 추후 데이터베이스 호출 시 사용
    

# # DB 종속성
# def get_db():
# 	# 새로운 세션 생성
# 	db = SessionLocal()
# 	try:
# 		# 세션 사용
# 		yield db
# 	finally:
# 		# 세션 종료
# 		db.close()


# ==================================================================================
# Revision - 비동기 설정
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncAttrs
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy.exc import OperationalError



# 비동기 엔진 설정
	# 비동기 지원 DB 드라이버
DATABASE_URL = "sqlite+aiosqlite:///./DealMakers.db"

# 비동기 엔진 사용
engine = create_async_engine(
    DATABASE_URL, 
    echo=True
)

# 비동기 세션로컬 객체 생성
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    # DB 객체 유지
    expire_on_commit=False
)

# 데이터베이스 객체 생성
class Base(AsyncAttrs, DeclarativeBase):
    # AsyncAttrs : ORM 객체에서 .await() 메서드를 사용할 수 있도록 함
    # DeclarativeBase : 모든 ORM 모델(테이블)의 부모 클래스 역할
		# DB 테이블 생성
    pass

## 비동기 DB 초기화
async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        assert engine.url.database, "Database URL is not set or connection failed."
    except OperationalError as e:
        raise AssertionError(f"Database connection failed: {e}")
    

## 비동기 DB 종속성 함수
	# async with 구문 자체가 예외가 발생해도 자동으로 정리(cleanup)함
    # 예외가 발생해도 세션(db)이 자동으로 닫힘
async def async_get_db():
    async with AsyncSessionLocal() as db:
        yield db