import streamlit as st
from helper.script_loader import load_file

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

    col_building, col_room, col_camera = st.columns([1, 1, 1])
    
    if "selected_building" not in st.session_state:
        st.session_state.selected_building = None

    # =====================
    # TÒA NHÀ
    # =====================
    
    buildings = [
        "Giảng đường A",
        "Giảng đường B",
        "Giảng đường E",
        "Giảng đường Nguyễn Đăng",
        "Tòa nhà trung tâm"
    ]

    with col_building:

        header_col, btn_col = st.columns([3, 1])

        with header_col:
            st.subheader("Tòa nhà")
        
        with btn_col:
            st.button(":material/add: Thêm", key="add_building")

        for building in buildings:
            with st.container(border = True):
                info_col, edit_col, power_col, delete_col = st.columns(
                    [3.7, 1, 1, 1]
                )

                with info_col:
                    st.write(building)
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

        if st.session_state.selected_building:

            st.success(
                f"Tòa nhà đang chọn: {st.session_state.selected_building}"
            )

            rooms = ["P101", "P102", "P103"]

            for room in rooms:
                st.container(border=True).write(room)

        else:
            st.info("Chọn một tòa nhà để xem danh sách phòng.")

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