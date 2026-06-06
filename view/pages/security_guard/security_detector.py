import streamlit as st

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

        # Khởi tạo ma trận lưới 2x2 để hiển thị 4 góc Camera
        grid_row1_col1, grid_row1_col2 = st.columns(2)
        grid_row2_col1, grid_row2_col2 = st.columns(2)

        # --- CAMERA 01: BÀN GIÁO VIÊN ---
        with grid_row1_col1:
            st.markdown("""
                <div class="cam-box cam-bg-wood">
                    <div class="cam-badge-title">Cam 01 - Bàn giáo viên</div>
                    <div class="cam-badge-status status-live">TRỰC TIẾP</div>
                    <div class="cam-info-footer">FPS: 30<br>Độ trễ: 12ms</div>
                </div>
            """, unsafe_allow_html=True)

        # --- CAMERA 02: CUỐI LỚP ---
        with grid_row1_col2:
            st.markdown("""
                <div class="cam-box cam-bg-gray">
                    <div class="cam-badge-title">Cam 02 - Cuối lớp</div>
                    <div class="cam-badge-status status-live">TRỰC TIẾP</div>
                    <div class="cam-info-footer">FPS: 30<br>Độ trễ: 12ms</div>
                </div>
            """, unsafe_allow_html=True)

        # --- CAMERA 03: CỬA CHÍNH ---
        with grid_row2_col1:
            st.markdown("""
                <div class="cam-box cam-bg-brown">
                    <div class="cam-badge-title">Cam 03 - Cửa chính</div>
                    <div class="cam-badge-status status-live">TRỰC TIẾP</div>
                    <div class="cam-info-footer">FPS: 30<br>Độ trễ: 12ms</div>
                </div>
            """, unsafe_allow_html=True)

        # --- CAMERA 04: CỬA PHỤ (TRẠNG THÁI NGHỈ / TẮT) ---
        with grid_row2_col2:
            st.markdown("""
                <div class="cam-box cam-bg-dark">
                    <div class="cam-badge-title">Cam 04 - Cửa phụ</div>
                    <div class="cam-badge-status status-idle">NGHỈ</div>
                    <div class="cam-info-footer">FPS: 30<br>Độ trễ: 12ms</div>
                </div>
            """, unsafe_allow_html=True)

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
