import streamlit as st
from view.component.sidebar.supervision import get_selection
from view.component.header import show_header
from view.pages.detector import show_detector
from view.pages.logs import show_logs
from view.pages.field_report import show_report 

def show_supervision_dashboard():
    show_header()
    col1, col2 = st.columns([1,4])
    with col1:
        selected = get_selection()
    with col2:
        if selected == "Giám sát trực tiếp":
            show_detector()
        elif selected == "Nhật ký vi phạm":
            show_logs()
        elif selected == "Xuất biên bản":
            show_report()



