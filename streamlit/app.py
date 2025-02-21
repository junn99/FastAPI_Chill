import streamlit as st

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None, "Brand", "Manufacturer", "Admin"]


def login():
    st.header("로그인")
    role = st.selectbox("역할을 선택하세요", ROLES)

    if st.button("로그인"):
        st.session_state.role = role
        st.rerun()


def logout():
    st.session_state.role = None
    st.rerun()


role = st.session_state.role

logout_page = st.Page(logout, title="로그아웃", icon=":material/logout:")
settings = st.Page("settings.py", title="설정", icon=":material/settings:")

brand_1 = st.Page(
    "brand/brand_info.py",
    title="브랜드 정보",
    icon=":material/business:",
    default=(role == "Brand"),
)
brand_2 = st.Page(
    "brand/brand_project.py", 
    title="프로젝트 관리", 
    icon=":material/work:"
)
respond_1 = st.Page(
    "respond/respond_info.py",
    title="제조사 정보",
    icon=":material/factory:",
    default=(role == "Manufacturer"),
)
respond_2 = st.Page(
    "respond/respond_projects.py", 
    title="진행 중인 프로젝트", 
    icon=":material/engineering:"
)
admin_1 = st.Page(
    "admin/admin_brands.py",
    title="브랜드 관리",
    icon=":material/supervised_user_circle:",
    default=(role == "Admin"),
)
admin_2 = st.Page(
    "admin/admin_manufacturers.py", 
    title="제조사 관리", 
    # icon=":material/factory_settings:"
)

account_pages = [logout_page, settings]
brand_pages = [brand_1, brand_2]
manufacturer_pages = [respond_1, respond_2]
admin_pages = [admin_1, admin_2]

st.title("브랜드 매니저")
# st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")

page_dict = {}
if st.session_state.role in ["Brand", "Admin"]:
    page_dict["브랜드"] = brand_pages
if st.session_state.role in ["Manufacturer", "Admin"]:
    page_dict["제조사"] = manufacturer_pages
if st.session_state.role == "Admin":
    page_dict["관리자"] = admin_pages

if len(page_dict) > 0:
    pg = st.navigation({"계정": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()