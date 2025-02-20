# 데이터베이스 내에서 어떤 종류의 테이블을 만들 건지
# 데이터베이스 모델 = 테이블 안에 있는 실제 레코드

# 1. Base를 불러와야 함.
from database import Base
    # 데이터베이스를 위한 모델을 만들어야 함

# 2. 테이블 정의
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey # 레코드 속성


# todos.db 쓸 때 모델
# class Todos(Base):
#     # SQLAlchemy가 추후 데이터베이스에서 이 테이블 이름을 찾는 방법
#     __tablename__ ="todos"
    
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String)
#     description = Column(String)
#     priority = Column(Integer)
#     complete = Column(Boolean, default=False)



# todosapp.db에 들어갈 추가 모델
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)    
    phone_number = Column(String)

class Todos(Base):
    __tablename__ ="todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    # 사용자의 기본 키가 todos 테이블 내의 소유주 id와 일치
    owner_id = Column(Integer, ForeignKey("users.id"))
