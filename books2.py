from fastapi import FastAPI, Path, Query, HTTPException
# Path : 경로 유효성 검사
# Query : 쿼리 매개변수에 대한 유효성 검사
# HTTPException : 예외처리
    # 메서드 내에서 발생시켜야 함.
from pydantic import BaseModel, Field
# Field : 필드에 유효성 검사 추가할 수 있게

from starlette import status
# 기존엔 api 요청이 성공하면 200을 반환하는 것이 끝
# 좀 더 구체적인 상황을 전달할 수 있음

from typing import Optional


app = FastAPI()

class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    # 객체 초기화
    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_date = published_date

# 유효성 검사
# 책 요청을 유효성 검사 : 책 요청이 일치하면 책으로 바꿀 수 있고, 책은 목록에 저장
class BookRequest(BaseModel):
    # POST작업에선 필요가 없기때문에 option
    # but? 삭제나 업데이트할 땐 필요
    id: Optional[int] = Field(description="ID is not needed on create",
                              default=None)
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    # 스웨거에서 보여지는 거 정의
    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "condingwithroby",
                "description": "A new description of a book",
                "rating": 5,
                "published_date": 2029
            }
        }
    }




BOOKS = [
    Book(1,'Conputer Science Pro', 'codingwithroby', 'A very nice book!', 5, 2020),
    Book(2,'Be Fast with FastAPI', 'codingwithroby', 'A great book!', 5, 2018),
    Book(3,'Master Endpoints', 'codingwithroby', 'A awesome book!', 5, 2010),
    Book(4,'HP1', 'Author 1', 'Book Description', 2, 2015),
    Book(5,'HP2', 'Author 2', 'Book Description', 3, 2020),
    Book(6,'HP3', 'Author 3', 'Book Description', 1, 2025),
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def read_all_books():
    return BOOKS

# 특정 목록 불러오기
@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
# Path(gt=0) : URL 매개변수에서 경로 매개 변수로 통과
# -> 0보다 크거나 오류를 반환해야 함. 
# 사용자가 앱의 경로 매개변수를 입력할 때, 그 경로 매개변수가 유효한지 판단, 앱 실행전에
# 그리고 BookRequest를 여기선 사용하지 않았기 때문에, 따로따로 하려면 Path사용해야 함
async def read_book(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book
    raise HTTPException(status_code=404, 
                        detail="Item not found")
        
# read_book이랑 경로는 같지만, 쿼리이므로 패스랑 겹치진 않게됨
@app.get("/books/", status_code=status.HTTP_200_OK)
async def read_book_rating(book_rating: int = Query(gt=0, lt=6)):
    books_to_return = []
    for book in BOOKS:
        if book.rating == book_rating:
            books_to_return.append(book)
    return books_to_return

@app.get("/books/publish", status_code=status.HTTP_200_OK)
async def read_books_by_publish_date(published_date: int = Query(gt=1999, 
                                                               lt=2031)):
    books_to_return = []
    for book in BOOKS:
        if book.published_date == published_date:
            books_to_return.append(book)
    return books_to_return


# 어떤 데이터도 반환하지 않음, 그거 바꾸는 것 뿐 = HTTP_201_CREATED
@app.post("/books/create_book",status_code=status.HTTP_201_CREATED)
# async def create_book(book_request = Body()):
# 유효성 검사
# 위에작업까진 그냥 요청 적은 거 다 보냄, 거름망 필요
async def create_book(book_request: BookRequest):
    # 이제 검증을 통해 해당 항목이 BookRequest과 일치하는 지 확인
    # 형식화된 요청

    # 새 책에 새 변수 생성
    new_book = Book(**book_request.model_dump())
        # book_request.model_dump(): Pydantic 객체를 Python 딕셔너리로 변환
        # **는 언패킹 연산자
            # dict의 각 key-value를 Book 클래스의 생성자에 전달하는 역할
    print(type(new_book)) # >>> <class 'books2.Book'>
    BOOKS.append(find_book_id(new_book))


# DB가 없는 지금은 id가 자동적으로 올라가지 않으므로, 그 과정 해줌
def find_book_id(book: Book):
    # if len(BOOKS) > 0:
    #     book.id = BOOKS[-1].id + 1
    # else:
    #     book.id = 1

    # 위의 거 요약문
    book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    return book


# PUT
# 모델(BookRequest) 정의 시, id는 선택값이지만
# 함수에서 id를 사용하므로 그대로 써야함
# 이것 역시 반환하는 것 없음 = HTTP_204_NO_CONTENT
@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    # 업데이트 유무
    book_change = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book.id:
            BOOKS[i] = book
            # 업데이트 됨
            book_change=True
    # 이것 역시 id가 없을 때나 책이 존재하지 않을 때 명시 필요
    if not book_change:
        raise HTTPException(status_code=404,
                            detail="Item not found")


# DELETE
# id를 사용한다면 Path로 유효성 검사 필요
    # 근데 중복되는 거 같은데
# 이것도 데이터를 반환하지 않고, 그저 삭제니깐 = HTTP_204_NO_CONTENT
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_change = False
    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_change=True
            break
    if not book_change:
        raise HTTPException(status_code=404,
                            detail="Item not found")



# 오류 & 예외 처리 = Status Code
# 1. 책(사용자)이 존재하지 않을 때
# 2. id에 대한 유효성 검사 = 범위 안에 있는지
