from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. FastAPI의 app이 데이터베이스 위치를 만드는 데 사용
# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todos.db'
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'

# 2. app을 위한 엔진 설정 : 데이터베이스 사용
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread":False})
    # 하나의 스레드만 확인하는 것을 방지, DB에선 여러 스레드가 발생할 수 있음

# 3. 세션 로컬 생성
    # 세션 로컬의 인스턴스마다 데이터베이스 세션을 갖게 됨
SessionLocal = sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine)

# 4. 데이터베이스 객체 만들기
# 추후 데이터베이스를 호출 할 수 있음
Base = declarative_base()