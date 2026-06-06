import streamlit as st
import datetime
from helper.script_loader import load_file

def show_report():
    
    css = load_file("view/style/style.css")

    st.markdown("<h2 class='page-main-title'>Xuất biên bản ca thi</h2>", unsafe_allow_html=True)
        
    st.markdown(f"""
        <style>
            {css}
        </style>
    """, unsafe_allow_html = True)
    _, form_center, _ = st.columns([1, 2, 1])
    with form_center:
        with st.container(border=True):
            st.text_input("Môn thi", value="Tin học đại cương")
            st.text_input("Phòng thi", value="Giảng đường Nguyễn Đăng - ND.202")
            st.text_area("Ghi chú giáo viên", value="Danh sách vi phạm do giáo viên ghi nhận và xác nhận trong ca thi.", height=120)
                
            st.write("")
            btn1, btn2 = st.columns(2)
            btn1.button(":material/picture_as_pdf: XUẤT BIÊN BẢN PDF", use_container_width=True, type="primary", key="ex_pdf")
            btn2.button(":material/table_view: XUẤT EXCEL", key="ex_excel")
