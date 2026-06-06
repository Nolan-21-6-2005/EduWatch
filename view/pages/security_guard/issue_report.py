from helper.script_loader import load_file
import streamlit as st
import datetime

st.set_page_config(layout="wide", page_title="Báo cáo sự cố")

def show_issue_report():
    # ==========================================
    # 1. CẤU HÌNH TRANG TỔNG (AN MẶC ĐỊNH & ÉP DARK THEME)
    # ==========================================

    css = load_file("view/style/style.css")

    st.markdown(f"""
        <style>
            {css}
        </style>
    """, unsafe_allow_html=True)

    # ==========================================
    # 2. KHU VỰC TRẠNG CHÍNH ĐỘC LẬP
    # ==========================================
    st.markdown('<h2 class="section-title">Báo cáo sự cố</h2>', unsafe_allow_html=True)
    
    # --- KHUNG FORM NHẬP LIỆU ---
    with st.container():
        st.markdown('<div class="custom-card-form">', unsafe_allow_html=True)
        
        st.selectbox("Tòa nhà", ["Giảng đường A", "Giảng đường B", "Giảng đường Nguyễn Đăng"])
        st.selectbox("Phòng", ["ND.202", "ND.206", "ND.102"])
        st.text_input("Loại sự cố", placeholder="Nhập loại sự cố (Ví dụ: Camera offline, Mất nguồn...)")
        st.text_area("Mô tả sự cố", placeholder="Mô tả chi tiết tình trạng sự cố kỹ thuật...", height=120)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🛫 GỬI BÁO CÁO", type="primary")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # --- KHUNG LỊCH SỬ BÁO CÁO ---
    st.markdown('<h2 class="section-title" style="font-size: 20px; margin-top: 20px;">Lịch sử báo cáo sự cố</h2>', unsafe_allow_html=True)
    
    st.markdown("""
        <table class="history-table">
            <thead>
                <tr>
                    <th>Thời gian gửi</th>
                    <th>Loại sự cố</th>
                    <th>Nội dung / Vị trí</th>
                    <th>Trạng thái xử lý</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="color: #8B949E;">2026-05-16 08:34:30</td>
                    <td style="font-weight: 700; color: #FFFFFF;">Camera offline</td>
                    <td>Giảng đường Nguyễn Đăng - ND.202 - Camera offline: gggg</td>
                    <td><span class="status-badge-waiting">Chờ xử lý</span></td>
                </tr>
            </tbody>
        </table>
    """, unsafe_allow_html=True)
