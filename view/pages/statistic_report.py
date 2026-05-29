import streamlit as st
import datetime
from utils.load_css import apply_css

def show_report():
    # --- Cấu hình trang ---
    st.set_page_config(layout="wide", page_title="EduWatch VNUA Admin")
    backdground_color = st.get_option("theme.backgroundColor")

    apply_css("view/style/report_style.css")
    # --- CSS Tùy biến ---
    st.markdown(f"""
        <style>
        .stat-card {{
            background-color: {backdground_color}; 
        }}
        .custom-table {{
            background-color: {backdground_color};
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # --- MAIN CONTENT (Khu vực nội dung chính phía bên phải) ---
    # Tiêu đề trang chính và cụm nút Xuất file
    title_col1, title_col2 = st.columns([3, 1])

    with title_col1:
        st.markdown(
            "<h2 style='color: #2CA854; margin: 0;'>Thống kê báo cáo</h2>",
            unsafe_allow_html=True,
        )

    with title_col2:
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            st.button(":material/picture_as_pdf: XUẤT PDF", width="content", type="primary")
        with btn_col2:
            st.button(":material/table_view: EXCEL", width="content")


    # Khu vực 2 thẻ thông báo vi phạm (Thống kê nhanh)
    st.markdown("<br>", unsafe_allow_html=True)
    card_col1, card_col2 = st.columns(2)

    with card_col1:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-title">VI PHẠM PHỔ BIẾN PHÒNG THƯỜNG</div>
                <div class="stat-content">Sử dụng điện thoại (6)</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with card_col2:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-title">VI PHẠM PHỔ BIẾN PHÒNG THI</div>
                <div class="stat-content">Quay bài/Trao đổi (7)</div>
            </div>
        """,
            unsafe_allow_html=True,
        )


    # Thanh Bộ lọc Tìm kiếm theo ngày
    filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 4])

    with filter_col1:
        # Set mặc định ngày 27/05/2026 như trong hình
        d = st.date_input(
            "Ngày báo cáo", datetime.date(2026, 5, 27), label_visibility="collapsed"
        )

    with filter_col2:
        st.button(":material/search: TÌM KIẾM", type="primary")


    # Khu vực Bảng dữ liệu thống kê chi tiết
    st.markdown(
        """
        <table class="custom-table">
            <thead>
                <tr>
                    <th>TÒA NHÀ</th>
                    <th>PHÒNG HỌC</th>
                    <th>SỐ VI PHẠM PHÒNG THƯỜNG</th>
                    <th>SỐ VI PHẠM PHÒNG THI</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="font-weight: bold;">Giảng đường A</td>
                    <td>ND.202</td>
                    <td style="font-weight: bold;">3</td>
                    <td style="font-weight: bold;">1</td>
                </tr>
                <tr>
                    <td style="font-weight: bold;">Giảng đường B</td>
                    <td>ND.206</td>
                    <td style="font-weight: bold;">1</td>
                    <td style="font-weight: bold;">4</td>
                </tr>
                <tr>
                    <td style="font-weight: bold;">Giảng đường Nguyễn Đăng</td>
                    <td>ND.202</td>
                    <td style="font-weight: bold;">2</td>
                    <td style="font-weight: bold;">0</td>
                </tr>
                <tr>
                    <td style="font-weight: bold;">Tòa nhà trung tâm</td>
                    <td>ND.206</td>
                    <td style="font-weight: bold;">0</td>
                    <td style="font-weight: bold;">2</td>
                </tr>
            </tbody>
        </table>
    """,
        unsafe_allow_html=True,
    )
