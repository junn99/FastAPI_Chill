# 관리자만 endpoints들을 실행해 볼 수 있게 설정
# models.py에서 Users모델을 보면 role 테이블이 있음
# 지금까진 JWT로 사용자 이름과 아이디로만 인코딩 함
# auth.py에서 create_access_token에서 role도 추가를 해야함.
    # 다른 곳도 추가 ㅇㅇ
from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from starlette import status
from database import SessionLocal
from .auth import get_current_user


router = APIRouter(
    prefix='/admin',
    tags=['admin']
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




@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency,
                   db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401,
                            detail="Autentication Failed")
    return db.query(Todos).all()


# exmapleuser1

@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
                      db: db_dependency,
                      todo_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, 
                            detail="Autentication Failed")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, 
                            detail="Todo not found.")
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()