import streamlit as st
import pandas as pd
from datetime import datetime
from utils.database import (
    get_brand_by_name,
    get_brand_projects,
    add_project,
    update_project,
    delete_project,
    query_to_dataframe
)

def app():
    st.title("프로젝트 관리")
    
    # 현재 로그인한 역할 확인
    role = st.session_state.role
    
    if role not in ["Brand", "Admin"]:
        st.error("이 페이지에 접근할 권한이 없습니다.")
        return
    
    # 사용자 식별 (실제 구현에서는 로그인 시스템과 연동)
    if role == "Brand":
        # 로그인한 브랜드 선택 (실제 구현에서는 로그인 시 자동으로 설정)
        # 임시로 선택 UI 제공
        brand_list = query_to_dataframe("SELECT id, name FROM brands")
        
        if len(brand_list) == 0:
            st.info("등록된 브랜드가 없습니다. 먼저 브랜드 정보를 등록해주세요.")
            return
        else:
            selected_brand = st.selectbox(
                "브랜드 선택", 
                options=brand_list['name'].tolist(),
                index=0
            )
    else:  # Admin
        # 관리자는 모든 브랜드를 선택할 수 있음
        brand_list = query_to_dataframe("SELECT id, name FROM brands")
        
        if len(brand_list) == 0:
            st.info("등록된 브랜드가 없습니다. 먼저 브랜드 정보를 등록해주세요.")
            return
        else:
            selected_brand = st.selectbox(
                "브랜드 선택", 
                options=brand_list['name'].tolist(),
                index=0
            )
    
    # 선택한 브랜드의 ID 가져오기
    brand_info = get_brand_by_name(selected_brand)
    
    if brand_info.empty:
        st.error("브랜드 정보를 찾을 수 없습니다.")
        return
    
    brand_id = brand_info.iloc[0]['id']
    
    # 탭 생성
    tab1, tab2 = st.tabs(["프로젝트 목록", "새 프로젝트 등록"])
    
    with tab1:
        st.subheader(f"{selected_brand}의 프로젝트 목록")
        
        # 브랜드의 프로젝트 목록 가져오기
        projects = get_brand_projects(brand_id)
        
        if projects.empty:
            st.info("등록된 프로젝트가 없습니다.")
        else:
            # 표시할 프로젝트 목록 정리
            projects_display = projects[['id', 'name', 'start_date', 'end_date', 'status']]
            projects_display.columns = ['ID', '프로젝트명', '시작일', '종료일', '상태']
            
            st.dataframe(projects_display, use_container_width=True)
            
            # 프로젝트 선택 및 상세 정보 표시
            selected_project_id = st.selectbox(
                "상세 정보를 볼 프로젝트 선택",
                options=projects['id'].tolist(),
                format_func=lambda x: projects.loc[projects['id'] == x, 'name'].iloc[0]
            )
            
            selected_project = projects[projects['id'] == selected_project_id]
            
            if not selected_project.empty:
                with st.expander("프로젝트 상세 정보", expanded=True):
                    with st.form("project_edit_form"):
                        project_name = st.text_input(
                            "프로젝트명", 
                            value=selected_project.iloc[0]['name']
                        )
                        
                        description = st.text_area(
                            "프로젝트 설명", 
                            value=selected_project.iloc[0]['description'] if pd.notna(selected_project.iloc[0]['description']) else ""
                        )
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            start_date = st.date_input(
                                "시작일", 
                                value=datetime.strptime(selected_project.iloc[0]['start_date'], '%Y-%m-%d').date() 
                                if pd.notna(selected_project.iloc[0]['start_date']) else datetime.now().date()
                            )
                        
                        with col2:
                            end_date = st.date_input(
                                "종료일", 
                                value=datetime.strptime(selected_project.iloc[0]['end_date'], '%Y-%m-%d').date() 
                                if pd.notna(selected_project.iloc[0]['end_date']) else datetime.now().date()
                            )
                        
                        status_options = ["계획", "진행 중", "완료", "보류", "취소"]
                        status = st.selectbox(
                            "상태", 
                            options=status_options,
                            index=status_options.index(selected_project.iloc[0]['status']) 
                            if pd.notna(selected_project.iloc[0]['status']) and selected_project.iloc[0]['status'] in status_options 
                            else 0
                        )
                        
                        requirements = st.text_area(
                            "요구사항", 
                            value=selected_project.iloc[0]['requirements'] if pd.notna(selected_project.iloc[0]['requirements']) else ""
                        )
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            update_button = st.form_submit_button("정보 업데이트")
                        
                        with col2:
                            delete_button = st.form_submit_button(
                                "프로젝트 삭제", 
                                type="primary",
                                help="이 작업은 되돌릴 수 없습니다. 신중하게 진행하세요."
                            )
                        
                    if update_button:
                        update_project(
                            selected_project_id,
                            project_name,
                            description,
                            start_date.strftime('%Y-%m-%d'),
                            end_date.strftime('%Y-%m-%d'),
                            status,
                            requirements
                        )
                        st.success("프로젝트 정보가 업데이트되었습니다.")
                        st.rerun()
                    
                    if delete_button:
                        delete_project(selected_project_id)
                        st.success("프로젝트가 삭제되었습니다.")
                        st.rerun()
    
    with tab2:
        st.subheader("새 프로젝트 등록")
        
        with st.form("new_project_form"):
            new_project_name = st.text_input("프로젝트명 *", help="프로젝트명은 필수 항목입니다.")
            new_description = st.text_area("프로젝트 설명")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_start_date = st.date_input("시작일", value=datetime.now().date())
            
            with col2:
                new_end_date = st.date_input("종료일", value=datetime.now().date())
            
            new_status_options = ["계획", "진행 중", "완료", "보류", "취소"]
            new_status = st.selectbox("상태", options=new_status_options, index=0)
            
            new_requirements = st.text_area("요구사항")
            
            submit_button = st.form_submit_button("프로젝트 등록")
            
            if submit_button:
                if not new_project_name:
                    st.error("프로젝트명을 입력해주세요.")
                else:
                    add_project(
                        brand_id,
                        new_project_name,
                        new_description,
                        new_start_date.strftime('%Y-%m-%d'),
                        new_end_date.strftime('%Y-%m-%d'),
                        new_status,
                        new_requirements
                    )
                    st.success(f"프로젝트 '{new_project_name}'이(가) 등록되었습니다.")
                    st.rerun()

if __name__ == "__main__":
    app()
else:
    app()