from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from starlette import status
# 요청에 대한 사용자 이름과 암호를 얻을 수 있음
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
    # Endpoint를 위한 종속성 주입으로 사용해야 함.
    # OAuth2 암호 요청 양식으로 사용자 이름과 암호 사용
    # OAuth2PasswordBearer
        # FastAPI에게 요청을 처리하기 전에 전달자 토큰을 확인함.
from jose import jwt, JWTError
    # 비밀키와 알고리즘이 필요함
from datetime import timedelta, datetime

router = APIRouter(
    # 이 파일에서 모든 api endpoint는 /auth로 시작
    prefix='/auth',
    # swagger 문서 상에서 구분되는 태그
    tags=['auth']
)

# 그냥 키 설정 이므로 아무거나 지정하면 됨 : openssl rand -hex 32
SECRET_KEY = '6837ab0fb4b0f4dd293016039a002e76bac916a66b8e873644f8d5f82ee6f0aa'
ALGORITHM='HS256'

# CryptContext를 bcrypt로 사용할 새 변수 생성
bcrypt_context = CryptContext(schemes=['bcrypt'],
                              deprecated="auto")
# API 요청에 종속성을 부여하기 위해 토큰을 확인해야 함
# prifix로 endpoint가 바뀌면 같이 바꿔줘야 함
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')
    # tokenUrl : 클라이언트가 토큰을 요청하는 엔드포인트의 경로
    # POST 요청을 보낼 URL을 지정
    # /auth/token 엔드포인트에서 로그인을 처리하고 JWT 토큰을 발급해 줘야함.


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


class Token(BaseModel):
    access_token: str
    token_type: str




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



# 사용자 인증값이 db와 맞는지 확인하는 함수 = 사용자가 입력한 비밀번호가 맞는지 확인하
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        # 유저가 존재하지 않으면 False 반환.
        return False
    # 유저가 입력한 비번을 해시하여 DB의 해시된 비번과 비교
    if not bcrypt_context.verify(password, user.hashed_password):
        # 유저가 존재하지만 비밀번호가 틀리면 False 반환.
        return False
    # 유저가 존재하고, 비밀번호도 맞으면 user 객체를 반환
    return user

# 엑세스 토큰 생성
def create_access_token(username: str, user_id: int,
                        expires_delta: timedelta):
    # JWT에 추가할 인코딩 생성
    encode = {'sub': username, 'id': user_id}
    # 만료된 토큰 찾았을 때
    expires = datetime.now() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    # Depends(oauth2_bearer) : 사용자를 먼저 확보해 전달되는 토큰 확인
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validation user.")
        return {"username": username, 'id': user_id}
    # JWT 오류가 나도 똑같은 HTTP 예외를 표시하고 싶음
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validation user.")



@router.post("/", status_code=status.HTTP_201_CREATED)
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
# 1. 사용자 이름과 비밀번호 입력받아서 인증
# 2. JWT를 사용해서 사용자 이름과 비번을 암호화 
@router.post("/token", response_model=Token)
    # response_model를 적용하면 반환값이 무조건 모델대로 나와야 함
    # 아니면 에러 발생
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    # Depends()를 사용하면 FastAPI가 자동으로 요청의 바디에서 username과 password를 추출
    # 클라이언트가 POST 요청을 보내면 FastAPI가 자동으로 OAuth2PasswordRequestForm 객체를 만들어서 form_data에 넣어줌.
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Could not validation user.")
    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    return {"access_token": token, 'token_type': 'bearer'}