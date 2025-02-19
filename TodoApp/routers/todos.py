from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from starlette import status
from database import SessionLocal


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


@router.get("/")
async def read_all(db: db_dependency):
    # Todos 테이블의 모든 데이터를 조회
    return db.query(Todos).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found.")

#POST
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.dict())
    db.add(todo_model)
    db.commit()


# PUT
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, 
                      todo_request: TodoRequest,
                      todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
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
async def delete_todo(db: db_dependency,
                      todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404,
                            detail="Todo not found.")
    
    db.query(Todos).filter(Todos.id == todo_id).delete()

    db.commit()



# 앱 실행
if __name__=="__main__":
    import uvicorn
    uvicorn.run("main:router", reload=True)
        # 여기 한 개 더 있어야 하는데