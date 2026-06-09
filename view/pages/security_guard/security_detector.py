import streamlit as st
from src.frontend.camera_request import connect_camera

st.set_page_config(layout="wide", page_title="EduWatch VNUA - Bảo vệ")

def show_security_detector():
    # ==========================================
    # 1. CẤU HÌNH TỔNG & STYLE DARK THEME CHUẨN
    # ==========================================

    css = load_file("view/style/style.css")

    st.markdown(f"""
        <style>
            {css}
        </style>
    """, unsafe_allow_html=True)

    # ==========================================
    # 2. PHÂN CHIA BỐ CỤC CHÍNH (3 CỘT)
    # ==========================================
    # Cột 1: Sidebar (1.2) | Cột 2: Lưới Camera (3.2) | Cột 3: Trạng thái (1.1)
    col_main_cam, col_right_status = st.columns([3, 1])
    # ------------------------------------------
    # CỘT 2: KHU VỰC BỘ LỌC & LƯỚI CAMERA
    # ------------------------------------------
    with col_main_cam:
        # Bộ lọc Tòa nhà / Phòng học
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            st.selectbox("Tòa nhà", ["Giảng đường A", "Giảng đường B", "Giảng đường Nguyễn Đăng"])
        with filter_col2:
            st.selectbox("Phòng học", ["ND.202", "ND.206", "ND.102"])
            
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

        connect_camera()
    # ------------------------------------------
    # CỘT 3: PANEL TRẠNG THÁI CAMERA (BÊN PHẢI)
    # ------------------------------------------
    with col_right_status:
        # Tạo một khoảng trống đầu cột để cân đối hàng lối với lưới camera
        st.markdown("<div style='margin-top: 52px;'></div>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="status-panel">
                <div class="status-panel-title">TRẠNG THÁI CAMERA</div>
                
                <div class="status-row">
                    <span class="status-name">Bàn giáo viên</span>
                    <span class="badge-pill pill-active">Hoạt động</span>
                </div>
                
                <div class="status-row">
                    <span class="status-name">Cuối lớp</span>
                    <span class="badge-pill pill-active">Hoạt động</span>
                </div>
                
                <div class="status-row">
                    <span class="status-name">Cửa chính</span>
                    <span class="badge-pill pill-active">Hoạt động</span>
                </div>
                
                <div class="status-row">
                    <span class="status-name">Cửa phụ</span>
                    <span class="badge-pill pill-error">Mất kết nối</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
