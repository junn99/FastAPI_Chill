import streamlit as st
import pandas as pd
import os
from utils.database import get_connection, DB_PATH

def app():
    st.title("설정")
    
    # 현재 역할 확인
    role = st.session_state.role
    
    # 탭 생성
    tab1, tab2 = st.tabs(["계정 정보", "데이터베이스 관리"])
    
    with tab1:
        st.subheader("계정 정보")
        st.write(f"현재 로그인: {role or '없음'}")
        
        if role:
            st.write("역할별 권한:")
            
            if role == "Brand":
                st.info("""
                **브랜드 계정 권한**
                - 브랜드 정보 조회 및 수정
                - 프로젝트 등록, 수정, 삭제
                """)
            elif role == "Manufacturer":
                st.info("""
                **제조사 계정 권한**
                - 제조사 정보 조회 및 수정
                - 프로젝트 제안 확인 및 응답
                - 진행 중인 프로젝트 관리
                """)
            elif role == "Admin":
                st.info("""
                **관리자 계정 권한**
                - 모든 브랜드 및 제조사 정보 관리
                - 모든 프로젝트 관리
                - 시스템 설정 관리
                """)
    
    with tab2:
        st.subheader("데이터베이스 관리")
        
        if role == "Admin":
            st.write(f"데이터베이스 파일 위치: {os.path.abspath(DB_PATH)}")
            
            # 테이블 통계 정보
            conn = get_connection()
            
            brand_count = pd.read_sql_query("SELECT COUNT(*) as count FROM brands", conn).iloc[0]['count']
            project_count = pd.read_sql_query("SELECT COUNT(*) as count FROM projects", conn).iloc[0]['count']
            manufacturer_count = pd.read_sql_query("SELECT COUNT(*) as count FROM manufacturers", conn).iloc[0]['count']
            
            st.write("데이터베이스 통계:")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("브랜드 수", brand_count)
            
            with col2:
                st.metric("프로젝트 수", project_count)
            
            with col3:
                st.metric("제조사 수", manufacturer_count)
            
            # 데이터베이스 백업 및 초기화 옵션
            st.divider()
            st.subheader("데이터베이스 관리 옵션")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("데이터베이스 백업", help="현재 데이터베이스 상태를 백업 파일로 저장합니다."):
                    import shutil
                    from datetime import datetime
                    
                    # 백업 파일 생성
                    backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                    backup_path = f"data/backups/brand_manager_{backup_time}.db"
                    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
                    
                    # 데이터베이스 파일 복사
                    shutil.copy2(DB_PATH, backup_path)
                    st.success(f"데이터베이스가 성공적으로 백업되었습니다: {backup_path}")
            
            with col2:
                if st.button("샘플 데이터 생성", help="테스트용 샘플 데이터를 생성합니다."):
                    # 샘플 데이터 생성 함수 호출
                    create_sample_data()
                    st.success("샘플 데이터가 생성되었습니다.")
                    st.rerun()
            
            # 데이터베이스 초기화 (위험한 작업)
            st.divider()
            with st.expander("⚠️ 데이터베이스 초기화 (위험)", expanded=False):
                st.warning("이 작업은 모든 데이터를 삭제합니다. 이 작업은 되돌릴 수 없습니다.")
                
                confirmation = st.text_input("초기화를 진행하려면 'INITIALIZE'를 입력하세요")
                
                if st.button("데이터베이스 초기화") and confirmation == "INITIALIZE":
                    conn.close()  # 연결 닫기
                    
                    # 기존 DB 파일 삭제
                    if os.path.exists(DB_PATH):
                        os.remove(DB_PATH)
                    
                    # 새 DB 초기화
                    from utils.database import init_database
                    init_database()
                    
                    st.success("데이터베이스가 초기화되었습니다.")
                    st.rerun()
        else:
            st.info("데이터베이스 관리 기능은 관리자만 사용할 수 있습니다.")

def create_sample_data():
    """테스트용 샘플 데이터 생성"""
    from utils.database import add_brand, add_project, execute_query
    
    # 샘플 브랜드 추가
    sample_brands = [
        {
            "name": "패션라이프",
            "contact_person": "김지민",
            "phone": "010-1234-5678",
            "email": "jimin@fashionlife.com",
            "address": "서울시 강남구 테헤란로 123",
            "registration_number": "123-45-67890",
            "description": "최신 트렌드를 반영한 패션 브랜드입니다."
        },
        {
            "name": "에코스타일",
            "contact_person": "이서연",
            "phone": "010-9876-5432",
            "email": "seoyeon@ecostyle.com",
            "address": "서울시 성동구 왕십리로 45",
            "registration_number": "987-65-43210",
            "description": "환경 친화적인 소재를 사용하는 지속 가능한 패션 브랜드입니다."
        },
        {
            "name": "모던테일러",
            "contact_person": "박준호",
            "phone": "010-5555-7777",
            "email": "junho@moderntailor.com",
            "address": "서울시 마포구 와우산로 29",
            "registration_number": "555-77-99999",
            "description": "맞춤형 정장과 캐주얼 의류를 제공하는 브랜드입니다."
        }
    ]
    
    # 브랜드 ID 저장
    brand_ids = {}
    
    for brand in sample_brands:
        add_brand(
            brand["name"],
            brand["contact_person"],
            brand["phone"],
            brand["email"],
            brand["address"],
            brand["registration_number"],
            brand["description"]
        )
        
        # 브랜드 ID 가져오기
        query = "SELECT id FROM brands WHERE name = ?"
        result = execute_query(query, (brand["name"],), fetch=True)
        brand_ids[brand["name"]] = result[0][0]
    
    # 샘플 프로젝트 추가
    sample_projects = [
        {
            "brand_name": "패션라이프",
            "name": "여름 컬렉션 2025",
            "description": "다가오는 여름 시즌을 위한 경량 의류 컬렉션",
            "start_date": "2025-01-15",
            "end_date": "2025-05-30",
            "status": "진행 중",
            "requirements": "친환경 소재 사용, 15개 이상의 디자인 필요"
        },
        {
            "brand_name": "패션라이프",
            "name": "가을 아우터 컬렉션",
            "description": "2025년 가을 시즌 아우터웨어 라인업",
            "start_date": "2025-03-01",
            "end_date": "2025-07-30",
            "status": "계획",
            "requirements": "방수 및 방풍 소재 사용, 최소 10개 디자인"
        },
        {
            "brand_name": "에코스타일",
            "name": "재활용 데님 프로젝트",
            "description": "재활용 면과 폐기 데님을 활용한 지속 가능한 의류 라인",
            "start_date": "2025-02-01",
            "end_date": "2025-06-30",
            "status": "진행 중",
            "requirements": "100% 재활용 소재 사용, 자원 절약형 생산 공정"
        },
        {
            "brand_name": "모던테일러",
            "name": "비즈니스 캐주얼 라인",
            "description": "현대적인 직장인을 위한 편안한 비즈니스 캐주얼 의류",
            "start_date": "2025-01-10",
            "end_date": "2025-04-15",
            "status": "진행 중",
            "requirements": "신축성 있는 소재, 세탁 용이성, 다양한 사이즈 제공"
        }
    ]
    
    for project in sample_projects:
        add_project(
            brand_ids[project["brand_name"]],
            project["name"],
            project["description"],
            project["start_date"],
            project["end_date"],
            project["status"],
            project["requirements"]
        )
    
    # 샘플 제조사 추가
    sample_manufacturers = [
        {
            "name": "대한봉제",
            "contact_person": "최민준",
            "phone": "010-1111-2222",
            "email": "minjun@daehan.com",
            "address": "서울시 중구 을지로 45",
            "capacity": "월 5,000 pcs",
            "specialties": "니트웨어, 캐주얼 의류"
        },
        {
            "name": "그린팩토리",
            "contact_person": "정소민",
            "phone": "010-3333-4444",
            "email": "somin@greenfactory.com",
            "address": "경기도 부천시 원미구 중동 123",
            "capacity": "월 3,000 pcs",
            "specialties": "친환경 의류, 재활용 소재 가공"
        },
        {
            "name": "정밀어패럴",
            "contact_person": "한도윤",
            "phone": "010-7777-8888",
            "email": "doyun@jungmil.com",
            "address": "인천시 남동구 남동대로 789",
            "capacity": "월 8,000 pcs",
            "specialties": "정장, 코트, 고급 의류"
        }
    ]
    
    for manufacturer in sample_manufacturers:
        query = """
        INSERT INTO manufacturers (name, contact_person, phone, email, address, capacity, specialties)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(
            query, 
            (
                manufacturer["name"],
                manufacturer["contact_person"],
                manufacturer["phone"],
                manufacturer["email"],
                manufacturer["address"],
                manufacturer["capacity"],
                manufacturer["specialties"]
            )
        )

if __name__ == "__main__":
    app()