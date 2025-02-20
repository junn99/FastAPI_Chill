from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from starlette import status
from database import SessionLocal

# 사용자 기능을 통해 JWT 인증을 할 수 있으니 todo로 연동
from .auth import get_current_user


router = APIRouter()

# DB Dependency
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
### 유저 종속성 = 사용자 의존성
    # 사용자 먼저 유효성 검사를 받게 함
user_dependency = Annotated[dict, Depends(get_current_user)]


# Pydantic request
from pydantic import BaseModel, Field

# models.py에서 Todos 모델 참고
# id는 넘기지 않음 = 기본 키니깐 = 자동 증분
class TodoRequest(BaseModel):
# Field : 유효성 검사
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, 
                   db: db_dependency, ):
    if user is None:
        raise HTTPException(status_code=401, detail="Autentication Failed")
    # Todos 테이블의 모든 데이터를 조회
    # return db.query(Todos).all()

    # 유저에 따른 필터로 모든 데이터 조회
    return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency,
                    db: db_dependency, 
                    todo_id: int = Path(gt=0)):
    # 사용자 종속성과 세트 구문
    if user is None:
        raise HTTPException(status_code=401, detail="Autentication Failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found.")

#POST
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency,
                        # 현재 사용자를 확보할 때 종속성 주입에서 반환된 정보 가짐
                        # Swagger에서 확인할 때 잠금 표시 : 사용자 인증 필요
                      db: db_dependency, 
                      todo_request: TodoRequest):
    # 1. 해당 사용자가 유효한 지 확인
    if user is None:
        raise HTTPException(status_code=401, detail="Autentication Failed")
    # 2. todo_request를 변환한 후에도 todo_model은 owner_id를 가지지 않음
        # owner_id : 외래키
        # 그래서 추가 필요
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))
        # 사용자 id와 같은 걸로 owner_id도 추가

    db.add(todo_model)
    db.commit()


# PUT
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency,
                      db: db_dependency, 
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Autentication Failed")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()
    
# DELETE
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency,
                      db: db_dependency,
                      todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Autentication Failed")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404,
                            detail="Todo not found.")
    
    db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('id')).delete()

    db.commit()



# 앱 실행
if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:router", reload=True)
        # 여기 한 개 더 있어야 하는데