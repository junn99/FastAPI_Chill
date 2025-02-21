import streamlit as st
import pandas as pd
import plotly.express as px
from utils.database import (
    query_to_dataframe,
    execute_query
)

def app():
    st.title("브랜드 관리")
    
    # 현재 로그인한 역할 확인
    role = st.session_state.role
    
    if role != "Admin":
        st.error("이 페이지는 관리자만 접근할 수 있습니다.")
        return
    
    # 탭 생성
    tab1, tab2 = st.tabs(["브랜드 목록", "통계 및 분석"])
    
    with tab1:
        st.subheader("브랜드 목록")
        
        # 모든 브랜드 정보 가져오기
        query = """
        SELECT b.*, 
               (SELECT COUNT(*) FROM projects WHERE brand_id = b.id) as project_count
        FROM brands b
        ORDER BY b.name
        """
        brands = query_to_dataframe(query)
        
        if brands.empty:
            st.info("등록된 브랜드가 없습니다.")
        else:
            # 표시할 브랜드 목록 정리
            display_df = brands[['id', 'name', 'contact_person', 'phone', 'email', 'project_count']]
            display_df.columns = ['ID', '브랜드명', '담당자', '연락처', '이메일', '프로젝트 수']
            
            st.dataframe(display_df, use_container_width=True)
            
            # 브랜드 선택 및 상세 정보 표시
            selected_brand_id = st.selectbox(
                "상세 정보를 볼 브랜드 선택",
                options=brands['id'].tolist(),
                format_func=lambda x: brands.loc[brands['id'] == x, 'name'].iloc[0]
            )
            
            selected_brand = brands[brands['id'] == selected_brand_id]
            
            if not selected_brand.empty:
                with st.expander("브랜드 상세 정보", expanded=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**브랜드명:** {selected_brand.iloc[0]['name']}")
                        st.write(f"**담당자:** {selected_brand.iloc[0]['contact_person'] if pd.notna(selected_brand.iloc[0]['contact_person']) else '미지정'}")
                        st.write(f"**연락처:** {selected_brand.iloc[0]['phone'] if pd.notna(selected_brand.iloc[0]['phone']) else '미지정'}")
                        st.write(f"**이메일:** {selected_brand.iloc[0]['email'] if pd.notna(selected_brand.iloc[0]['email']) else '미지정'}")
                    
                    with col2:
                        st.write(f"**주소:** {selected_brand.iloc[0]['address'] if pd.notna(selected_brand.iloc[0]['address']) else '미지정'}")
                        st.write(f"**사업자등록번호:** {selected_brand.iloc[0]['registration_number'] if pd.notna(selected_brand.iloc[0]['registration_number']) else '미지정'}")
                        st.write(f"**등록일:** {selected_brand.iloc[0]['created_at']}")
                        st.write(f"**프로젝트 수:** {selected_brand.iloc[0]['project_count']}")
                    
                    st.write(f"**기업 소개:**")
                    st.write(selected_brand.iloc[0]['description'] if pd.notna(selected_brand.iloc[0]['description']) else '정보 없음')
                    
                    # 브랜드의 프로젝트 목록
                    st.subheader("브랜드 프로젝트")
                    
                    query = """
                    SELECT p.id, p.name, p.start_date, p.end_date, p.status,
                           (SELECT COUNT(*) FROM project_manufacturers WHERE project_id = p.id) as manufacturer_count
                    FROM projects p
                    WHERE p.brand_id = ?
                    ORDER BY p.start_date DESC
                    """
                    brand_projects = query_to_dataframe(query, (selected_brand_id,))
                    
                    if brand_projects.empty:
                        st.info("등록된 프로젝트가 없습니다.")
                    else:
                        display_projects = brand_projects[['id', 'name', 'start_date', 'end_date', 'status', 'manufacturer_count']]
                        display_projects.columns = ['ID', '프로젝트명', '시작일', '종료일', '상태', '참여 제조사 수']
                        
                        st.dataframe(display_projects, use_container_width=True)
    
    with tab2:
        st.subheader("브랜드 통계 및 분석")
        
        # 프로젝트 수에 따른 브랜드 통계
        query = """
        SELECT b.name, COUNT(p.id) as project_count
        FROM brands b
        LEFT JOIN projects p ON b.id = p.brand_id
        GROUP BY b.id
        ORDER BY project_count DESC
        """
        brand_stats = query_to_dataframe(query)
        
        if not brand_stats.empty:
            # 프로젝트 수에 따른 브랜드 차트
            fig = px.bar(
                brand_stats, 
                x='name', 
                y='project_count',
                title='브랜드별 프로젝트 수',
                labels={'name': '브랜드명', 'project_count': '프로젝트 수'},
                color='project_count',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 브랜드 등록 추이
            query = """
            SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as brand_count
            FROM brands
            GROUP BY month
            ORDER BY month
            """
            registration_trend = query_to_dataframe(query)
            
            if not registration_trend.empty and len(registration_trend) > 1:
                fig = px.line(
                    registration_trend,
                    x='month',
                    y='brand_count',
                    title='월별 브랜드 등록 추이',
                    labels={'month': '월', 'brand_count': '브랜드 수'},
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # 프로젝트 상태 분포
            query = """
            SELECT status, COUNT(*) as count
            FROM projects
            GROUP BY status
            """
            status_dist = query_to_dataframe(query)
            
            if not status_dist.empty:
                fig = px.pie(
                    status_dist,
                    values='count',
                    names='status',
                    title='프로젝트 상태 분포',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("통계를 생성하기 위한 충분한 데이터가 없습니다.")

if __name__ == "__main__":
    app()