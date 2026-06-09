import streamlit as st
from helper.script_loader import load_file
from utils.list import (
    option,
    building_map
)
from src.database_query.buildings_manager import  (
    get_buildings,
    get_cameras,
    get_rooms
)

st.set_page_config(layout="wide", page_title="Quản lý tòa nhà")

def show_buildings():
    # --- Cấu hình trang ---

    # --- CSS Tùy biến (Đồng bộ với giao diện trước) ---
    css = load_file("view/style/style.css")
    
    st.markdown(f"""
        <style>
            {css}
        </style>
    """, unsafe_allow_html=True)
    
    # --- MAIN CONTENT ---
    # Tiêu đề chính
    st.markdown("<h2 style='color: #2CA854; margin-bottom: 5px;'>Danh sách tòa nhà</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #7A869A; font-size: 14px;'>Quản lý tòa nhà, phòng và góc camera theo cấu trúc dữ liệu hiện có.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    page = st.pills(
        "Navigation",
        ["Home", "Settings", "About"],
        selection_mode="multi",
        default="Home",
        label_visibility="collapsed"
    )
    if page == "Home":
        st.write("Home content")

    elif page == "Settings":
        st.write("Settings content")

    elif page == "About":
        st.write("About content")
    
    option = st.selectbox(
        "Lọc theo tòa nhà", (
            "Giảng đường Cơ điện cũ", 
            "Giảng đường Cơ điện mới", 
            "Giảng đường Giảng đường A",
            "Giảng đường Giảng đường B",
            "Giảng đường Giảng đường C",
            "Giảng đường Nguyễn Đăng",
            "Giảng đường Giảng đường E"
        ),
    )

    building_map = {
        "Giảng đường Cơ điện cũ": 1,
        "Giảng đường Cơ điện mới": 2,
        "Giảng đường Giảng đường A": 3,
        "Giảng đường Giảng đường B": 4,
        "Giảng đường Giảng đường C": 5,
        "Giảng đường Nguyễn Đăng": 6,
        "Giảng đường Giảng đường E": 7
    }

    col_building, col_room, col_camera = st.columns([1, 1, 1])
    

    if "selected_building" not in st.session_state:
        st.session_state.selected_building = None

    # =====================
    # TÒA NHÀ
    # =====================

    with col_building:

        header_col, btn_col = st.columns([3, 1])

        with header_col:
            st.subheader("Tòa nhà")
        
        with btn_col:
            st.button(":material/add: Thêm", key="add_building")

        for building in get_buildings(building_map[option]):
            with st.container(border = True):
                info_col, edit_col, power_col, delete_col = st.columns(
                    [3.7, 1, 1, 1]
                )

                with info_col:
                    st.write(building[0])
                    st.caption("Đang hoạt động")

                with edit_col:
                    st.button(":material/edit:", key=f"edit_{building}")

                with power_col:
                    st.button(":material/power_settings_new:", key=f"power_{building}")

                with delete_col:
                    st.button(":material/delete:", key=f"delete_{building}")
    # =====================
    # PHÒNG
    # =====================
    with col_room:
        header_col, btn_col = st.columns([3, 1])
        
        with header_col:
            st.subheader("Phòng")

        with btn_col:
            st.button(":material/add: Thêm", key="add_room")

        for room in get_rooms(building_map[option]):
            with st.container(border = True):
                info_col, edit_col, power_col, delete_col = st.columns(
                    [3.7, 1, 1, 1]
                )

                with info_col:
                    st.write(building[0])
                    st.caption("Đang hoạt động")

                with edit_col:
                    st.button(":material/edit:", key=f"edit_{building}")

                with power_col:
                    st.button(":material/power_settings_new:", key=f"power_{building}")

                with delete_col:
                    st.button(":material/delete:", key=f"delete_{building}")

    # =====================
    # CAMERA
    # =====================
    with col_camera:
        header_col, btn_col = st.columns([3, 1])
        
        with header_col:
            st.subheader("Góc camera")
        with btn_col:
            st.button(":material/add: Thêm", key = "add_camera")
        st.info("Chọn một phòng để xem danh sách góc camera.")