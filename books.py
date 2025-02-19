from fastapi import FastAPI

app = FastAPI()

BOOKS = [
    {"title": "Title One", "author": "Author One", "category": "science"},
    {"title": "Title Two", "author": "Author Two", "category": "science"},
    {"title": "Title Three", "author": "Author Three", "category": "history"},
    {"title": "Title Four", "author": "Author Four", "category": "math"},
    {"title": "Title Five", "author": "Author Five", "category": "math"},
    {"title": "Title Six", "author": "Author Two", "category": "math"},

]


# 클라이언트가 이 파이썬 함수를 사용할 수 있도록 endpoint 추가
@app.get("/api-endpoint")
async def first_api():
    return {"message": "Hello jun!"}

# 정적 경로 : 변경x
@app.get("/books")
async def read_all_books():
    return BOOKS

# Path Parameters : 동적 경로
# 각 책을 기반으로 endpoint만들 필요가 없음
# 사용자가 전달하는 모든 정보를 리턴하는 동적 경로 매개변수로 사용

# 순서 중요! 경로 매개변수는

### 이게 맞다
@app.get("/books/mybook")
async def read_all_books():
    return {"book_title": "My favorite Book"}

# @app.get("/books/{dynamic_param}")
# async def read_all_books(dynamic_param):
#     return {"dynamic_param" : dynamic_param}

# ## 순서상 No! : 동적 경로보다 앞에 와야함
# @app.get("/books/mybook")
# async def read_all_books():
#     return {"book_title": "My favorite Book"}

@app.get("/books/{book_title}")
async def read_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book
        

# Query Parameters
# 제공된 URL에 기반해 데이터를 필터링하는 방법
@app.get("/books/")
async def read_category_by_query(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


## 
@app.get("/books/{book_author}/")
async def read_author_category_by_query(book_author: str,
                                        category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == book_author.casefold() and \
        book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return
# GET request는 body가 없음



# POST : body에 데이터를 전송
# 리스트에 추가할 책 만들기
from fastapi import Body

@app.post("/books/create_book")
# 이 요청 본문 안에 새 책으로 변환하고 싶은 데이터가 있다는 것
async def create_book(new_book = Body()):
    BOOKS.append(new_book)


# PUT : body 가질 수 있음 = 업데이트
# 책을 보고 제목과 일치하는 곳을 찾아서 나머지 정보 바꿈
@app.put("/books/update_book")
async def update_book(updated_book=Body()):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == updated_book.get('title').casefold():
            BOOKS[i] = updated_book

# DELETE
@app.delete("/books/delete_book/{book_title}")
async def delete_book(book_title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get('title').casefold() == book_title.casefold():
            BOOKS.pop(i)
            break