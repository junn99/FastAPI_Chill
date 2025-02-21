import streamlit as st
import pandas as pd
from utils.database import (
    query_to_dataframe,
    execute_query
)

def app():
    st.title("진행 중인 프로젝트")
    
    # 현재 로그인한 역할 확인
    role = st.session_state.role
    
    if role not in ["Manufacturer", "Admin"]:
        st.error("이 페이지에 접근할 권한이 없습니다.")
        return
    
    # 제조사 선택 (실제 구현에서는 로그인 시 자동으로 설정)
    manufacturer_list = query_to_dataframe("SELECT id, name FROM manufacturers")
    
    if len(manufacturer_list) == 0:
        st.info("등록된 제조사가 없습니다. 먼저 제조사 정보를 등록해주세요.")
        return
    else:
        selected_manufacturer = st.selectbox(
            "제조사 선택", 
            options=manufacturer_list['name'].tolist(),
            index=0
        )
    
    # 선택한 제조사의 ID 가져오기
    selected_manufacturer_id = manufacturer_list[manufacturer_list['name'] == selected_manufacturer]['id'].iloc[0]
    
    # 탭 생성
    tab1, tab2 = st.tabs(["진행 중인 프로젝트", "새 프로젝트 제안"])
    
    with tab1:
        st.subheader(f"{selected_manufacturer}의 진행 중인 프로젝트")
        
        # 제조사가 참여하고 있는 프로젝트 목록 조회
        query = """
        SELECT p.id, b.name as brand_name, p.name as project_name, p.start_date, p.end_date, pm.status 
        FROM projects p
        JOIN brands b ON p.brand_id = b.id
        JOIN project_manufacturers pm ON p.id = pm.project_id
        WHERE pm.manufacturer_id = ?
        """
        active_projects = query_to_dataframe(query, (selected_manufacturer_id,))
        
        if active_projects.empty:
            st.info("현재 참여 중인 프로젝트가 없습니다.")
        else:
            # 표시할 프로젝트 목록 정리
            display_df = active_projects[['id', 'brand_name', 'project_name', 'start_date', 'end_date', 'status']]
            display_df.columns = ['ID', '브랜드', '프로젝트명', '시작일', '종료일', '진행 상태']
            
            st.dataframe(display_df, use_container_width=True)
            
            # 프로젝트 선택 및 상세 정보 표시
            if not active_projects.empty:
                selected_project_id = st.selectbox(
                    "상세 정보를 볼 프로젝트 선택",
                    options=active_projects['id'].tolist(),
                    format_func=lambda x: f"{active_projects[active_projects['id'] == x]['brand_name'].iloc[0]} - {active_projects[active_projects['id'] == x]['project_name'].iloc[0]}"
                )
                
                # 선택한 프로젝트의 자세한 정보 조회
                query = """
                SELECT p.*, b.name as brand_name, pm.status as collaboration_status, pm.notes
                FROM projects p
                JOIN brands b ON p.brand_id = b.id
                JOIN project_manufacturers pm ON p.id = pm.project_id
                WHERE p.id = ? AND pm.manufacturer_id = ?
                """
                project_details = query_to_dataframe(query, (selected_project_id, selected_manufacturer_id))
                
                if not project_details.empty:
                    with st.expander("프로젝트 상세 정보", expanded=True):
                        st.write(f"**브랜드:** {project_details.iloc[0]['brand_name']}")
                        st.write(f"**프로젝트명:** {project_details.iloc[0]['name']}")
                        st.write(f"**설명:** {project_details.iloc[0]['description'] if pd.notna(project_details.iloc[0]['description']) else '없음'}")
                        st.write(f"**시작일:** {project_details.iloc[0]['start_date']}")
                        st.write(f"**종료일:** {project_details.iloc[0]['end_date']}")
                        st.write(f"**프로젝트 상태:** {project_details.iloc[0]['status']}")
                        st.write(f"**요구사항:** {project_details.iloc[0]['requirements'] if pd.notna(project_details.iloc[0]['requirements']) else '없음'}")
                        
                        st.divider()
                        st.subheader("진행 상황 업데이트")
                        
                        with st.form("project_status_update"):
                            current_status = project_details.iloc[0]['collaboration_status']
                            
                            status_options = ["검토 중", "수락됨", "진행 중", "생산 완료", "출고 준비", "완료됨", "거절됨"]
                            new_status = st.selectbox(
                                "진행 상태", 
                                options=status_options,
                                index=status_options.index(current_status) if current_status in status_options else 0
                            )
                            
                            current_notes = project_details.iloc[0]['notes'] if pd.notna(project_details.iloc[0]['notes']) else ""
                            notes = st.text_area("메모/비고", value=current_notes)
                            
                            if st.form_submit_button("상태 업데이트"):
                                query = """
                                UPDATE project_manufacturers
                                SET status = ?, notes = ?
                                WHERE project_id = ? AND manufacturer_id = ?
                                """
                                execute_query(query, (new_status, notes, selected_project_id, selected_manufacturer_id))
                                st.success("프로젝트 상태가 업데이트되었습니다.")
                                st.rerun()
    
    with tab2:
        st.subheader("새 프로젝트 제안")
        
        # 제조사에게 아직 제안되지 않은 활성 프로젝트 조회
        query = """
        SELECT p.id, b.name as brand_name, p.name as project_name, p.description, p.start_date, p.end_date, p.status
        FROM projects p
        JOIN brands b ON p.brand_id = b.id
        WHERE p.id NOT IN (
            SELECT project_id FROM project_manufacturers WHERE manufacturer_id = ?
        )
        AND p.status IN ('계획', '진행 중')
        """
        available_projects = query_to_dataframe(query, (selected_manufacturer_id,))
        
        if available_projects.empty:
            st.info("현재 사용 가능한 새 프로젝트 제안이 없습니다.")
        else:
            st.write("다음 프로젝트에 참여할 수 있습니다:")
            
            # 표시할 프로젝트 목록 정리
            display_df = available_projects[['id', 'brand_name', 'project_name', 'start_date', 'end_date', 'status']]
            display_df.columns = ['ID', '브랜드', '프로젝트명', '시작일', '종료일', '상태']
            
            st.dataframe(display_df, use_container_width=True)
            
            # 프로젝트 선택 및 상세 정보 표시
            if not available_projects.empty:
                selected_project_id = st.selectbox(
                    "참여할 프로젝트 선택",
                    options=available_projects['id'].tolist(),
                    format_func=lambda x: f"{available_projects[available_projects['id'] == x]['brand_name'].iloc[0]} - {available_projects[available_projects['id'] == x]['project_name'].iloc[0]}",
                    key="new_project_select"
                )
                
                # 선택한 프로젝트의 자세한 정보 표시
                project_details = available_projects[available_projects['id'] == selected_project_id]
                
                if not project_details.empty:
                    st.write(f"**브랜드:** {project_details.iloc[0]['brand_name']}")
                    st.write(f"**프로젝트명:** {project_details.iloc[0]['project_name']}")
                    st.write(f"**설명:** {project_details.iloc[0]['description'] if pd.notna(project_details.iloc[0]['description']) else '없음'}")
                    
                    # 프로젝트에 참여하기
                    with st.form("join_project_form"):
                        status_options = ["검토 중", "수락됨", "거절됨"]
                        initial_status = st.selectbox("초기 상태", options=status_options, index=0)
                        
                        notes = st.text_area("메모/비고 (선택 사항)")
                        
                        if st.form_submit_button("프로젝트 참여 신청"):
                            # 프로젝트-제조사 연결 추가
                            query = """
                            INSERT INTO project_manufacturers (project_id, manufacturer_id, status, notes)
                            VALUES (?, ?, ?, ?)
                            """
                            execute_query(query, (selected_project_id, selected_manufacturer_id, initial_status, notes))
                            st.success(f"프로젝트 '{project_details.iloc[0]['project_name']}'에 성공적으로 참여 신청했습니다.")
                            st.rerun()

if __name__ == "__main__":
    app()
else:
    app()