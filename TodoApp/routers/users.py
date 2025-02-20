from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from models import Users
from starlette import status
from database import SessionLocal
from .auth import get_current_user

# 새 해시를 확인하고 생성할 수 있어야 함
from passlib.context import CryptContext


router = APIRouter(
    prefix='/user',
    tags=['user']
)

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 종속성 주입
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
# 해시 종속성 추가
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated="auto")



from pydantic import BaseModel, Field


# 왜 필요하지??
    # 비번 변경 시 요청 데이터를 검증
class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


# 사용자가 자신에 관한 모든 정보를 볼 수 있는
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_user(user: user_dependency,
                        db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    
    return db.query(Users).filter(Users.id == user.get('id')).first()

# 사용자 비번 업데이트
@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency,
                          db: db_dependency,
                          user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, 
                            detail="Autentication Failed")
    
    # 1. Users 모델 = 데이터베이스의 사용자 테이블
    # 2. user.get('id') = 현재 로그인한 사용자의 ID를 가져옴
    # 3. db.query(Users).filter(Users.id == user.get('id')).first()
        # 해당 ID에 맞는 유저 정보를 DB에서 가져옴
    #         {
    #     "id": 1,
    #     "username": "testuser",
    #     "hashed_password": "$2b$12$9kD6S..."
    #         }
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    # 사용자가 입력한 비밀번호가 실제 저장된 해시된 비밀번호와 일치하는지 검증
    if not bcrypt_context.verify(user_verification.password,
                                 user_model.hashed_password):
        raise HTTPException(status_code=401,
                            detail="Error on password change")
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()

# 사용자 폰번호 변경
@router.put("/phone/{phone_number}", status_code=status.HTTP_200_OK)
async def update_phone_number(user: user_dependency,
                              db: db_dependency,
                              phone_number: str):
    if user is None:
        raise HTTPException(status_code=401,
                            detail="Autentication Failed")

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.phone_number =  phone_number
    db.add(user_model)
    db.commit()