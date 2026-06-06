import streamlit as st
from helper.script_loader import load_file

st.set_page_config(layout="wide", page_title="Trạng thái thiết bị")

def show_device_state():
    # ==========================================
    # 1. CẤU HÌNH TỔNG & STYLE GIAO DIỆN SÁNG (LIGHT THEME)
    # ==========================================
    
    css = load_file("view/style/style.css")
    
    st.markdown(f"""
        <style>
            {css}
        </style>
    """, unsafe_allow_html=True)
    # ------------------------------------------
    # KHU VỰC HIỂN THỊ NỘI DUNG TRẠNG THÁI THIẾT BỊ
    # ------------------------------------------
    # Tiêu đề trang chức năng
    st.markdown("<div class='main-title'>Trạng thái thiết bị</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Chọn tòa nhà và phòng để xem danh sách camera. Bảo vệ chỉ có quyền xem trạng thái.</div>", unsafe_allow_html=True)

    # Khung card chứa bộ lọc địa điểm
    select_col1, select_col2 = st.columns(2)
    with select_col1:
        building = st.selectbox("Tòa nhà", ["Chọn tòa nhà", "Giảng đường A", "Giảng đường B", "Giảng đường Nguyễn Đăng"], index=0)
    with select_col2:
        # Nếu chưa chọn tòa nhà thì vô hiệu hóa (hoặc để trống) danh mục phòng
        room = st.selectbox("Phòng", ["Chọn phòng", "ND.202", "ND.206", "ND.102"], index=0)

    # Khung hiển thị danh sách thiết bị dạng bảng lưới
    st.markdown('<div class="data-card-box">', unsafe_allow_html=True)
    
    # Render thanh tiêu đề cột của bảng
    st.markdown("""
        <div class="table-header-grid">
            <div class="header-item">Tên Camera</div>
            <div class="header-item">Nguồn Camera</div>
            <div class="header-item">Trạng thái</div>
            <div class="header-item">Cập nhật lần cuối</div>
        </div>
    """, unsafe_allow_html=True)

    # Kiểm tra logic: Nếu người dùng chưa chọn tòa nhà hoặc chưa chọn phòng cụ thể
    if building == "Chọn tòa nhà" or room == "Chọn phòng":
        # Hiển thị thông báo yêu cầu chọn phòng y hệt bản thiết kế
        st.markdown("""
            <div class="empty-state-container">
                Chọn phòng để xem trạng thái camera.
            </div>
        """, unsafe_allow_html=True)
    else:
        # Nhánh hiển thị dữ liệu thực tế sau khi đã chọn phòng thành công (Ví dụ: Giảng đường A - ND.202)
        # Tạo style hàng dữ liệu cho bảng
        st.markdown("""
            <style>
            .table-row-grid {
                display: grid;
                grid-template-columns: 2fr 2fr 1.5fr 1.5fr;
                padding: 16px 24px;
                border-bottom: 1px solid #E2E8F0;
                align-items: center;
                background-color: #FFFFFF;
            }
            .table-row-grid:last-child { border-bottom: none; }
            .cell-text { font-size: 14px; color: #2D3748; font-weight: 500; }
            .cell-bold { font-weight: 600; color: #1A202C; }
            .status-badge {
                font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 12px; width: fit-content;
            }
            .status-online { background-color: #C6F6D5; color: #22543D; }
            .status-offline { background-color: #FED7D7; color: #742A2A; }
            </style>
            
            <div class="table-row-grid">
                <div class="cell-text cell-bold">Cam 01 - Bàn giáo viên</div>
                <div class="cell-text" style="color:#4A5568;">rtsp://192.168.1.101/stream1</div>
                <div><span class="status-badge status-online">Hoạt động</span></div>
                <div class="cell-text" style="color:#718096;">Vừa xong</div>
            </div>
            <div class="table-row-grid">
                <div class="cell-text cell-bold">Cam 02 - Cuối lớp</div>
                <div class="cell-text" style="color:#4A5568;">rtsp://192.168.1.102/stream1</div>
                <div><span class="status-badge status-online">Hoạt động</span></div>
                <div class="cell-text" style="color:#718096;">1 phút trước</div>
            </div>
            <div class="table-row-grid">
                <div class="cell-text cell-bold">Cam 03 - Cửa chính</div>
                <div class="cell-text" style="color:#4A5568;">rtsp://192.168.1.103/stream1</div>
                <div><span class="status-badge status-online">Hoạt động</span></div>
                <div class="cell-text" style="color:#718096;">3 phút trước</div>
            </div>
            <div class="table-row-grid">
                <div class="cell-text cell-bold">Cam 04 - Cửa phụ</div>
                <div class="cell-text" style="color:#4A5568;">rtsp://192.168.1.104/stream1</div>
                <div><span class="status-badge status-offline">Mất kết nối</span></div>
                <div class="cell-text" style="color:#742A2A; font-weight:600;">Mất tín hiệu</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

