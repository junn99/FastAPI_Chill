# 구조 순서

## 1. database.py
- 이건 거의 정해진 틀이라고 생각
    - 다만 실무에선 DB와 비동기면에서 살짝 다름
    - DB : SQLite -> Postgre
    - 비동기 적용 : sesstionmaker , db 비동기 종속성

## 2. models.py
- DB 테이블 정의

## 3. /routers

### 3-1. schemas.py
- API 모델 입력/응답 유효성 검증을 위한 클래스 정의
- 이거 솔직히 모르겠다..! 어떻게 바로 정의하지?
    - POST로 입력할 때, 어떤 값을 필수로 받아야 하는지
    - GET으로 조회할 땐, 어떤 값들이 보여야 하는지..! 

    그런 느낌이긴 한데 맞나?



### 3-2. crud.py
- 기본 동작 함수들 정의!
- 각 테이블(?)별로다가


### 3-3. brand API 기능 구현
- crud 참조해서 API endpoint 구현





## 마지막... main.py
- 모든 라우트 통합 & 실행

