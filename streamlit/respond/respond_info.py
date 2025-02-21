import streamlit as st
import pandas as pd
from utils.database import (
    query_to_dataframe,
    execute_query
)

def app():
    st.title("제조사 정보")
    
    # 현재 로그인한 역할 확인
    role = st.session_state.role
    
    if role not in ["Manufacturer", "Admin"]:
        st.error("이 페이지에 접근할 권한이 없습니다.")
        return
    
    # 제조사 선택 (실제 구현에서는 로그인 시 자동으로 설정)
    manufacturer_list = query_to_dataframe("SELECT id, name FROM manufacturers")
    
    if len(manufacturer_list) == 0:
        st.info("등록된 제조사가 없습니다. 새 제조사를 등록해주세요.")
        selected_manufacturer = None
    else:
        selected_manufacturer = st.selectbox(
            "제조사 선택", 
            options=manufacturer_list['name'].tolist(),
            index=0
        )
    
    # 탭 생성
    tab1, tab2 = st.tabs(["제조사 정보 조회/수정", "새 제조사 등록"])
    
    with tab1:
        if selected_manufacturer:
            # 선택한 제조사 정보 가져오기
            query = "SELECT * FROM manufacturers WHERE name = ?"
            manufacturer_info = query_to_dataframe(query, (selected_manufacturer,))
            
            if not manufacturer_info.empty:
                manufacturer_id = manufacturer_info.iloc[0]['id']
                
                with st.form("manufacturer_edit_form"):
                    st.subheader(f"{selected_manufacturer} 정보")
                    
                    contact_person = st.text_input(
                        "담당자 이름", 
                        value=manufacturer_info.iloc[0]['contact_person'] if pd.notna(manufacturer_info.iloc[0]['contact_person']) else ""
                    )
                    
                    phone = st.text_input(
                        "연락처", 
                        value=manufacturer_info.iloc[0]['phone'] if pd.notna(manufacturer_info.iloc[0]['phone']) else ""
                    )
                    
                    email = st.text_input(
                        "이메일", 
                        value=manufacturer_info.iloc[0]['email'] if pd.notna(manufacturer_info.iloc[0]['email']) else ""
                    )
                    
                    address = st.text_area(
                        "주소", 
                        value=manufacturer_info.iloc[0]['address'] if pd.notna(manufacturer_info.iloc[0]['address']) else ""
                    )
                    
                    capacity = st.text_input(
                        "생산 능력", 
                        value=manufacturer_info.iloc[0]['capacity'] if pd.notna(manufacturer_info.iloc[0]['capacity']) else "",
                        help="월 생산량 (예: 월 5,000 pcs)"
                    )
                    
                    specialties = st.text_area(
                        "전문 분야", 
                        value=manufacturer_info.iloc[0]['specialties'] if pd.notna(manufacturer_info.iloc[0]['specialties']) else "",
                        help="전문적으로 생산 가능한 의류 종류 (예: 니트웨어, 아우터, 데님)"
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        update_button = st.form_submit_button("정보 업데이트")
                    
                    with col2:
                        if role == "Admin":  # 관리자만 삭제 가능
                            delete_button = st.form_submit_button(
                                "제조사 삭제", 
                                type="primary",
                                help="이 작업은 되돌릴 수 없습니다. 신중하게 진행하세요."
                            )
                        
                if update_button:
                    query = """
                    UPDATE manufacturers 
                    SET contact_person = ?, phone = ?, email = ?, address = ?, capacity = ?, specialties = ? 
                    WHERE id = ?
                    """
                    execute_query(
                        query, 
                        (contact_person, phone, email, address, capacity, specialties, manufacturer_id)
                    )
                    st.success("제조사 정보가 업데이트되었습니다.")
                    st.rerun()
                
                if role == "Admin" and 'delete_button' in locals() and delete_button:
                    query = "DELETE FROM manufacturers WHERE id = ?"
                    execute_query(query, (manufacturer_id,))
                    st.success("제조사가 삭제되었습니다.")
                    st.rerun()
            else:
                st.error("제조사 정보를 찾을 수 없습니다.")
        else:
            st.info("제조사를 선택하거나 새 제조사를 등록해주세요.")
    
    with tab2:
        with st.form("new_manufacturer_form"):
            st.subheader("새 제조사 등록")
            
            new_manufacturer_name = st.text_input("제조사 이름 *", 
                                              help="제조사 이름은 필수 항목이며, 중복될 수 없습니다.")
            new_contact_person = st.text_input("담당자 이름")
            new_phone = st.text_input("연락처")
            new_email = st.text_input("이메일")
            new_address = st.text_area("주소")
            new_capacity = st.text_input("생산 능력", help="월 생산량 (예: 월 5,000 pcs)")
            new_specialties = st.text_area("전문 분야", help="전문적으로 생산 가능한 의류 종류 (예: 니트웨어, 아우터, 데님)")
            
            submit_button = st.form_submit_button("제조사 등록")
            
            if submit_button:
                if not new_manufacturer_name:
                    st.error("제조사 이름을 입력해주세요.")
                else:
                    # 이름 중복 확인
                    existing = query_to_dataframe(
                        "SELECT id FROM manufacturers WHERE name = ?", 
                        (new_manufacturer_name,)
                    )
                    
                    if not existing.empty:
                        st.error(f"제조사 '{new_manufacturer_name}'이(가) 이미 존재합니다.")
                    else:
                        query = """
                        INSERT INTO manufacturers (name, contact_person, phone, email, address, capacity, specialties)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """
                        execute_query(
                            query, 
                            (
                                new_manufacturer_name,
                                new_contact_person,
                                new_phone,
                                new_email,
                                new_address,
                                new_capacity,
                                new_specialties
                            )
                        )
                        st.success(f"제조사 '{new_manufacturer_name}'이(가) 등록되었습니다.")
                        st.rerun()

if __name__ == "__main__":
    app()
else:
    app()