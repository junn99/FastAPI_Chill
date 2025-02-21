import streamlit as st
import pandas as pd
from utils.api import (
    get_brands,
    get_brand_by_name,
    create_brand,
    update_brand,
    delete_brand,
)


def app():
    st.title("브랜드 정보")

    # 현재 로그인한 역할 확인
    role = st.session_state.role

    if role not in ["Brand", "Admin"]:
        st.error("이 페이지에 접근할 권한이 없습니다.")
        return

    # 브랜드 리스트 가져오기
    brands_data = get_brands()
    brand_list = pd.DataFrame(brands_data)

    # 사용자 식별 (실제 구현에서는 로그인 시스템과 연동)
    if role == "Brand":
        # 로그인한 브랜드 선택 (실제 구현에서는 로그인 시 자동으로 설정)
        # 임시로 선택 UI 제공
        if len(brand_list) == 0:
            st.info("등록된 브랜드가 없습니다. 새 브랜드를 등록해주세요.")
            selected_brand = None
            # 브랜드가 없으면 바로 등록 탭으로 이동
            show_register_tab = True
        else:
            selected_brand = st.selectbox(
                "브랜드 선택", options=brand_list["brand_name"].tolist(), index=0
            )
            # 브랜드가 이미 존재하면 등록 탭 숨기기
            show_register_tab = False
    else:  # Admin
        # 관리자는 모든 브랜드를 선택할 수 있음 + 항상 등록 탭 보이기
        if len(brand_list) == 0:
            st.info("등록된 브랜드가 없습니다. 새 브랜드를 등록해주세요.")
            selected_brand = None
        else:
            selected_brand = st.selectbox(
                "브랜드 선택", options=brand_list["brand_name"].tolist(), index=0
            )
        # 관리자는 항상 등록 탭을 볼 수 있음
        show_register_tab = True

    # 탭 생성 - 역할과 브랜드 등록 여부에 따라 다르게 표시
    if show_register_tab:
        tab1, tab2 = st.tabs(["브랜드 정보 조회/수정", "새 브랜드 등록"])
        active_tab = tab1
    else:
        # 브랜드가 이미 등록되어 있으면 조회/수정 탭만 표시
        tab1 = st.tabs(["브랜드 정보 조회/수정"])[0]
        active_tab = tab1

    with tab1:
        if selected_brand:
            # 선택한 브랜드 정보 가져오기
            brand_info = get_brand_by_name(selected_brand)

            if brand_info:
                brand_id = brand_info["id"]

                with st.form("brand_edit_form"):
                    st.subheader(f"{selected_brand} 정보")

                    brand_name = st.text_input(
                        "브랜드 이름",
                        value=(
                            brand_info["brand_name"] if brand_info["brand_name"] else ""
                        ),
                    )

                    capital = st.text_input(
                        "자본금",
                        value=brand_info["capital"] if brand_info["capital"] else "",
                    )

                    min_price = st.text_input(
                        "최소 단가",
                        value=(
                            brand_info["min_price"] if brand_info["min_price"] else ""
                        ),
                    )

                    max_price = st.text_input(
                        "최대 단가",
                        value=(
                            brand_info["max_price"] if brand_info["max_price"] else ""
                        ),
                    )

                    price = st.text_input(
                        "단가", value=brand_info["price"] if brand_info["price"] else ""
                    )

                    moq = st.text_area(
                        "MOQ", value=brand_info["moq"] if brand_info["moq"] else ""
                    )

                    planned_launch = st.text_input(
                        "납품 기한",
                        value=(
                            brand_info["planned_launch"]
                            if brand_info["planned_launch"]
                            else ""
                        ),
                    )

                    represetative_info = st.text_input(
                        "대표자 정보",
                        value=(
                            brand_info["represetative_info"]
                            if brand_info["represetative_info"]
                            else ""
                        ),
                    )

                    history = st.text_area(
                        "회사 연혁",
                        value=brand_info["history"] if brand_info["history"] else "",
                    )

                    performance = st.text_area(
                        "회사 실적",
                        value=(
                            brand_info["performance"]
                            if brand_info["performance"]
                            else ""
                        ),
                    )

                    marketing_plan = st.text_area(
                        "마케팅 계획",
                        value=(
                            brand_info["marketing_plan"]
                            if brand_info["marketing_plan"]
                            else ""
                        ),
                    )

                    business_plan = st.text_area(
                        "사업 계획",
                        value=(
                            brand_info["business_plan"]
                            if brand_info["business_plan"]
                            else ""
                        ),
                    )

                    col1, col2 = st.columns(2)

                    with col1:
                        update_button = st.form_submit_button("정보 업데이트")

                    with col2:
                        if role == "Admin":  # 관리자만 삭제 가능
                            delete_button = st.form_submit_button(
                                "브랜드 삭제",
                                type="primary",
                                help="이 작업은 되돌릴 수 없습니다. 신중하게 진행하세요.",
                            )

                if update_button:
                    updated_data = {
                        "brand_name": selected_brand,
                        "capital": capital,
                        "min_price": min_price,
                        "max_price": max_price,
                        "price": price,
                        "moq": moq,
                        "planned_launch": planned_launch,
                        "represetative_info": represetative_info,
                        "history": history,
                        "performance": performance,
                        "marketing_plan": marketing_plan,
                        "business_plan": business_plan,
                    }
                    update_brand(brand_id, updated_data)
                    st.success("브랜드 정보가 업데이트되었습니다.")
                    st.rerun()

                if role == "Admin" and "delete_button" in locals() and delete_button:
                    delete_brand(brand_id)
                    st.success("브랜드가 삭제되었습니다.")
                    st.rerun()
            else:
                st.error("브랜드 정보를 찾을 수 없습니다.")
        else:
            st.info("브랜드를 선택하거나 새 브랜드를 등록해주세요.")

    # 등록 탭은 조건에 따라 표시
    if show_register_tab:
        with tab2:
            with st.form("new_brand_form"):
                st.subheader("새 브랜드 등록")

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

                submit_button = st.form_submit_button("브랜드 등록")

                if submit_button:
                    if not new_brand_name:
                        st.error("브랜드 이름을 입력해주세요.")
                    else:
                        brand_data = {
                            "brand_name": new_brand_name,
                            "capital": new_capital,
                            "min_price": new_min_price,
                            "max_price": new_max_price,
                            "price": new_price,
                            "moq": new_moq,
                            "planned_launch": new_planned_launch,
                            "represetative_info": new_represetative_info,
                            "history": new_history,
                            "performance": new_performance,
                            "marketing_plan": new_marketing_plan,
                            "business_plan": new_business_plan,
                        }
                        success, response = create_brand(brand_data)

                        if success:
                            st.success(
                                f"브랜드 '{new_brand_name}'이(가) 등록되었습니다."
                            )
                            st.rerun()
                        else:
                            st.error(response)


if __name__ == "__main__":
    app()
else:
    # 모듈로 임포트되었을 때도 app() 함수를 직접 호출
    app()
