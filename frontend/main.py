import streamlit as st
import requests

# FastAPI 서버 주소
API_URL = "http://127.0.0.1:8000"




st.title("브랜드 프로젝트 생성")

with st.form("브랜드 등록 폼"):
    st.subheader("브랜드 정보 입력")


    # 웹에서_입력받을_정보 = st.text_input(
    #     "입력받을 정보",
    #     max_chars=100,
    #     placeholder="상자안에 지시사항 표시",
    #     help="주의사항 표시"
    #     )

    # # 이와 같은 형식으로 복사
    # 웹에서_입력받을_정보 = st.text_area("입력받을 정보",
    #                            height=100,
    #                            max_chars=100,
    #                            placeholder="상자안에 지시사항 표시",
    #                            help="상자 오른쪽 상단에 주의사항 표시"
    #                            )
    
    new_brand_name = st.text_input(
                    "브랜드 이름 *",
                    help="브랜드 이름은 필수 항목이며, 중복될 수 없습니다.",
                )
    new_capital = st.text_input("회사 자본")
    new_min_price = st.text_input("최소 단가")
    new_max_price = st.text_input("최대 단가")
    new_price = st.text_input("목표 단가")
    new_moq = st.text_input("MOQ")
    new_planned_launch = st.text_input("납품 기한")
    new_represetative_info = st.text_area("대표자 정보")
    new_history = st.text_input("회사 연혁")
    new_performance = st.text_area("회사 실적")
    new_marketing_plan = st.text_input("회사 마케팅 계획")
    new_business_plan = st.text_input("회사 사업 계획")
    



    submit_button = st.form_submit_button("입력 등록 버튼")



st.subheader("브랜드 목록 조회")
if st.button("조회하기"):
    # Streamlit이 FastAPI로 GET 요청을 보내고, 데이터를 받아오는 과정
    response = requests.get(f"{API_URL}/brand/read")
    if response.status_code == 200:
        # FastAPI에서 응답을 JSON 형태로 반환하기 때문에 response.json()을 사용하여 Python에서 사용할 수 있는 dict 형태로 변환
        brands = response.json()
        for i, brand in enumerate(brands):
            i += 1
            st.write(f"=== {i}번째 브랜드 ===\n\n**브랜드명**: {brand['brand_name']} \n\n**목표 단가**: {brand['price']} \n\n**MOQ**: {brand['moq']}")
        
    else: 
        st.error('브랜드 정보를 찾을 수 없습니다.')