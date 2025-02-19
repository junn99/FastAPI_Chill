from fastapi import APIRouter
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from starlette import status

router = APIRouter()

# CryptContext를 bcrypt로 사용할 새 변수 생성
bcrypt_context = CryptContext(schemes=['bcrypt'],
                              deprecated="auto")


# 필드 유효성 검사를 위한 pydantic 만들기
# 이것 역시 막 만드는게 아니라?
    # models.py에서 정의한 모델을 참조하여 만드는 것!
# id 는 자동증가(기본키)이므로 굳이 안적어도 됨
# is_active : 기본값으로 ture로 설정되있으므로 굳이 ㄴㄴ
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

# DB Dependency
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends

def get_db():
    # 요청이 올 때마다 새로운 DB 세션을 생성
    db = SessionLocal()
    # 응답을 반환하기 전 실행되는 코드
    try:
        # Depends(get_db)를 통해 데이터베이스 세션을 필요로 하는 엔드포인트에 주입
        yield db
    # 답변 전달한 후 실행
    finally:
        # 요청이 끝난 후 데이터베이스 연결을 닫는 역할
        db.close()


# @router.get("/")
# 종속성 주입 : 실행하려는 걸 실행하기 전에 뭔가를 해야 하게함.
# DB가 열리는 것에 의존
# 데이터베이스에서 모든 정보를 페치할 수 있음
# async def read_all(db: Annotated[Session, Depends(get_db)]):
#     return db.query(Todos).all()

# # 간략하게 줄일 수 있음

## 종속성
db_dependency = Annotated[Session, Depends(get_db)]




@router.post("/auth", status_code=status.HTTP_201_CREATED)
# CreateUserRequest : 사용자가 입력한 값이 우리의 양식에 맞는지 확인하기 위함
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    # create_user_model = Users(**create_user_request.model_dump())
        # 이 방법은 안됨
        # CreateUserRequest는 password를 가지지만
        # User 모델은 password가 아닌, hashed_password를 가지기때문
    # 그래서? 하나하나 다 명시해서 적어줘야 함
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        # hashed_password=create_user_request.password,
        # 해시화
        hashed_password=bcrypt_context.hash(create_user_request.password),
            # 해싱된 채로 DB에 저장
        is_active=True 
    )

    db.add(create_user_model)
    db.commit()


### 테스트 body
# {
#   "username": "codingwithroby",
#   "email": "codingwithroby@email.com",
#   "first_name": "Eric",
#   "last_name": "Roby",
#   "password": "test1234",
#   "role": "admin"
# }



# 사용자 인증
# 사용자 이름과 비밀번호 입력받아서 인증

@router.post("/token")
async def login_for_access_token():
    return 'token'