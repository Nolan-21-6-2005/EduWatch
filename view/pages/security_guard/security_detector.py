import streamlit as st

from src.frontend.camera_request import connect_camera

st.set_page_config(layout="wide", page_title="EduWatch VNUA - Bảo vệ")


def show_security_detector():
    col_main_cam, col_right_status = st.columns([3, 1], gap="medium")

    with col_main_cam:
        st.markdown(
            """
            <div class="page-header">
                <div>
                    <h1 class="page-header-title">Giám sát an ninh</h1>
                    <p class="page-header-subtitle">Theo dõi camera và trạng thái an ninh tại khu vực được chọn.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        filter_col1, filter_col2 = st.columns(2, gap="small")
        with filter_col1:
            st.selectbox("Tòa nhà", ["Giảng đường A", "Giảng đường B", "Giảng đường Nguyễn Đăng"])
        with filter_col2:
            st.selectbox("Phòng học", ["ND.202", "ND.206", "ND.102"])

        connect_camera()

    with col_right_status:
        st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="status-panel">
                <div class="status-panel-title">TRẠNG THÁI CAMERA</div>
                <div class="status-row"><span class="status-name">Bàn giáo viên</span><span class="badge-pill pill-active">Hoạt động</span></div>
                <div class="status-row"><span class="status-name">Cuối lớp</span><span class="badge-pill pill-active">Hoạt động</span></div>
                <div class="status-row"><span class="status-name">Cửa chính</span><span class="badge-pill pill-active">Hoạt động</span></div>
                <div class="status-row"><span class="status-name">Cửa phụ</span><span class="badge-pill pill-error">Mất kết nối</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
