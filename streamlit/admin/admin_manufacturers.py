import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import (
    query_to_dataframe,
    execute_query
)

def app():
    st.title("제조사 관리")
    
    # 현재 로그인한 역할 확인
    role = st.session_state.role
    
    if role != "Admin":
        st.error("이 페이지는 관리자만 접근할 수 있습니다.")
        return
    
    # 탭 생성
    tab1, tab2 = st.tabs(["제조사 목록", "협업 관리"])
    
    with tab1:
        st.subheader("제조사 목록")
        
        # 모든 제조사 정보 가져오기
        query = """
        SELECT m.*, 
               (SELECT COUNT(*) FROM project_manufacturers WHERE manufacturer_id = m.id) as project_count
        FROM manufacturers m
        ORDER BY m.name
        """
        manufacturers = query_to_dataframe(query)
        
        if manufacturers.empty:
            st.info("등록된 제조사가 없습니다.")
        else:
            # 표시할 제조사 목록 정리
            display_df = manufacturers[['id', 'name', 'contact_person', 'phone', 'email', 'project_count']]
            display_df.columns = ['ID', '제조사명', '담당자', '연락처', '이메일', '참여 프로젝트 수']
            
            st.dataframe(display_df, use_container_width=True)
            
            # 제조사 선택 및 상세 정보 표시
            selected_manufacturer_id = st.selectbox(
                "상세 정보를 볼 제조사 선택",
                options=manufacturers['id'].tolist(),
                format_func=lambda x: manufacturers.loc[manufacturers['id'] == x, 'name'].iloc[0]
            )
            
            selected_manufacturer = manufacturers[manufacturers['id'] == selected_manufacturer_id]
            
            if not selected_manufacturer.empty:
                with st.expander("제조사 상세 정보", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**제조사명:** {selected_manufacturer.iloc[0]['name']}")
                        st.write(f"**담당자:** {selected_manufacturer.iloc[0]['contact_person'] if pd.notna(selected_manufacturer.iloc[0]['contact_person']) else '미지정'}")
                        st.write(f"**연락처:** {selected_manufacturer.iloc[0]['phone'] if pd.notna(selected_manufacturer.iloc[0]['phone']) else '미지정'}")
                        st.write(f"**이메일:** {selected_manufacturer.iloc[0]['email'] if pd.notna(selected_manufacturer.iloc[0]['email']) else '미지정'}")
                    
                    with col2:
                        st.write(f"**주소:** {selected_manufacturer.iloc[0]['address'] if pd.notna(selected_manufacturer.iloc[0]['address']) else '미지정'}")
                        st.write(f"**생산 능력:** {selected_manufacturer.iloc[0]['capacity'] if pd.notna(selected_manufacturer.iloc[0]['capacity']) else '미지정'}")
                        st.write(f"**등록일:** {selected_manufacturer.iloc[0]['created_at']}")
                        st.write(f"**참여 프로젝트 수:** {selected_manufacturer.iloc[0]['project_count']}")
                    
                    st.write(f"**전문 분야:**")
                    st.write(selected_manufacturer.iloc[0]['specialties'] if pd.notna(selected_manufacturer.iloc[0]['specialties']) else '정보 없음')
                    
                    # 제조사가 참여 중인 프로젝트 목록
                    st.subheader("참여 중인 프로젝트")
                    
                    query = """
                    SELECT p.id, b.name as brand_name, p.name as project_name, 
                           p.start_date, p.end_date, pm.status
                    FROM project_manufacturers pm
                    JOIN projects p ON pm.project_id = p.id
                    JOIN brands b ON p.brand_id = b.id
                    WHERE pm.manufacturer_id = ?
                    ORDER BY p.start_date DESC
                    """
                    manufacturer_projects = query_to_dataframe(query, (selected_manufacturer_id,))
                    
                    if manufacturer_projects.empty:
                        st.info("참여 중인 프로젝트가 없습니다.")
                    else:
                        display_projects = manufacturer_projects[['id', 'brand_name', 'project_name', 'start_date', 'end_date', 'status']]
                        display_projects.columns = ['ID', '브랜드', '프로젝트명', '시작일', '종료일', '상태']
                        
                        st.dataframe(display_projects, use_container_width=True)
    
    with tab2:
        st.subheader("브랜드-제조사 협업 관리")
        
        # 모든 프로젝트-제조사 연결 정보 조회
        query = """
        SELECT pm.id, b.name as brand_name, p.name as project_name, 
               m.name as manufacturer_name, pm.status, pm.created_at
        FROM project_manufacturers pm
        JOIN projects p ON pm.project_id = p.id
        JOIN brands b ON p.brand_id = b.id
        JOIN manufacturers m ON pm.manufacturer_id = m.id
        ORDER BY pm.created_at DESC
        """
        collaborations = query_to_dataframe(query)
        
        if collaborations.empty:
            st.info("브랜드와 제조사 간의 협업 기록이 없습니다.")
        else:
            # 상태별 필터링 옵션
            all_statuses = collaborations['status'].unique().tolist()
            selected_status = st.multiselect(
                "상태별 필터링", 
                options=all_statuses,
                default=all_statuses
            )
            
            # 필터링된 데이터
            if selected_status:
                filtered_collaborations = collaborations[collaborations['status'].isin(selected_status)]
            else:
                filtered_collaborations = collaborations
            
            # 표시할 협업 목록 정리
            display_df = filtered_collaborations[['id', 'brand_name', 'project_name', 'manufacturer_name', 'status', 'created_at']]
            display_df.columns = ['ID', '브랜드', '프로젝트', '제조사', '상태', '연결일']
            
            st.dataframe(display_df, use_container_width=True)
            
            # 협업 상태 수정
            st.subheader("협업 상태 관리")
            
            selected_collaboration_id = st.selectbox(
                "관리할 협업 선택",
                options=filtered_collaborations['id'].tolist(),
                format_func=lambda x: f"{filtered_collaborations[filtered_collaborations['id'] == x]['brand_name'].iloc[0]} - " +
                                     f"{filtered_collaborations[filtered_collaborations['id'] == x]['project_name'].iloc[0]} - " +
                                     f"{filtered_collaborations[filtered_collaborations['id'] == x]['manufacturer_name'].iloc[0]}"
            )
            
            # 선택한 협업의 현재 정보
            selected_collaboration = filtered_collaborations[filtered_collaborations['id'] == selected_collaboration_id]
            
            if not selected_collaboration.empty:
                current_status = selected_collaboration.iloc[0]['status']
                
                # 협업 정보 수정
                query = """
                SELECT pm.*, p.name as project_name, b.name as brand_name, m.name as manufacturer_name
                FROM project_manufacturers pm
                JOIN projects p ON pm.project_id = p.id
                JOIN brands b ON p.brand_id = b.id
                JOIN manufacturers m ON pm.manufacturer_id = m.id
                WHERE pm.id = ?
                """
                collaboration_detail = query_to_dataframe(query, (selected_collaboration_id,))
                
                if not collaboration_detail.empty:
                    with st.form("collaboration_edit_form"):
                        st.write(f"**브랜드:** {collaboration_detail.iloc[0]['brand_name']}")
                        st.write(f"**프로젝트:** {collaboration_detail.iloc[0]['project_name']}")
                        st.write(f"**제조사:** {collaboration_detail.iloc[0]['manufacturer_name']}")
                        
                        status_options = ["검토 중", "수락됨", "진행 중", "생산 완료", "출고 준비", "완료됨", "거절됨", "취소됨"]
                        new_status = st.selectbox(
                            "협업 상태", 
                            options=status_options,
                            index=status_options.index(current_status) if current_status in status_options else 0
                        )
                        
                        current_notes = collaboration_detail.iloc[0]['notes'] if pd.notna(collaboration_detail.iloc[0]['notes']) else ""
                        notes = st.text_area("메모/비고", value=current_notes)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            update_button = st.form_submit_button("상태 업데이트")
                        
                        with col2:
                            delete_button = st.form_submit_button(
                                "협업 취소/삭제", 
                                type="primary",
                                help="이 작업은 되돌릴 수 없습니다. 신중하게 진행하세요."
                            )
                        
                        if update_button:
                            query = """
                            UPDATE project_manufacturers
                            SET status = ?, notes = ?
                            WHERE id = ?
                            """
                            execute_query(query, (new_status, notes, selected_collaboration_id))
                            st.success("협업 상태가 업데이트되었습니다.")
                            st.rerun()
                        
                        if delete_button:
                            query = "DELETE FROM project_manufacturers WHERE id = ?"
                            execute_query(query, (selected_collaboration_id,))
                            st.success("협업 관계가 삭제되었습니다.")
                            st.rerun()
            
            # 협업 통계
            st.subheader("협업 통계")
            
            # 상태별 협업 분포
            status_counts = filtered_collaborations['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            
            if not status_counts.empty:
                fig = px.pie(
                    status_counts,
                    values='count',
                    names='status',
                    title='협업 상태 분포',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 브랜드별 협업 수
                brand_collab = filtered_collaborations['brand_name'].value_counts().reset_index()
                brand_collab.columns = ['brand', 'count']
                
                fig = px.bar(
                    brand_collab,
                    x='brand',
                    y='count',
                    title='브랜드별 협업 수',
                    labels={'brand': '브랜드', 'count': '협업 수'},
                    color='count',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 제조사별 협업 수
                manufacturer_collab = filtered_collaborations['manufacturer_name'].value_counts().reset_index()
                manufacturer_collab.columns = ['manufacturer', 'count']
                
                fig = px.bar(
                    manufacturer_collab,
                    x='manufacturer',
                    y='count',
                    title='제조사별 협업 수',
                    labels={'manufacturer': '제조사', 'count': '협업 수'},
                    color='count',
                    color_continuous_scale='Teal'
                )
                st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    app()