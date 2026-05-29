import streamlit as st
import datetime
from utils.load_css import apply_css

def show_report():
    st.markdown("""
        <style>
        /* Ẩn hoàn toàn Sidebar mặc định của Streamlit */
        [data-testid="stSidebar"], section[data-testid="stSidebar"] {
            display: none !important;
            width: 0px !important;
        }
        /* Ẩn thanh Header trên cùng */
        [data-testid="stHeader"] {
            display: none !important;
        }
        /* Ẩn khoảng trống thừa phía trên cùng */
        [data-testid="stMainBlockContainer"] {
            padding-top: 2rem !important;
            max-width: 1350px !important;
            margin: 0 auto !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 class='page-main-title'>Xuất biên bản ca thi</h2>", unsafe_allow_html=True)
        
    _, form_center, _ = st.columns([1, 2, 1])
    with form_center:
        with st.container(border=True):
            st.text_input("Môn thi", value="Tin học đại cương")
            st.text_input("Phòng thi", value="Giảng đường Nguyễn Đăng - ND.202")
            st.text_area("Ghi chú giáo viên", value="Danh sách vi phạm do giáo viên ghi nhận và xác nhận trong ca thi.", height=120)
                
            st.write("")
            btn1, btn2 = st.columns(2)
            btn1.button("📄 XUẤT BIÊN BẢN PDF", use_container_width=True, type="primary", key="ex_pdf")
            btn2.button("📊 XUẤT EXCEL", use_container_width=True, key="ex_excel")
