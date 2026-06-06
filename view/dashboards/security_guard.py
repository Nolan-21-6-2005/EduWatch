import streamlit as st
from view.component.sidebar.security_guard import get_security_selection
from view.component.header import show_header
from view.pages.security_guard.security_detector import show_security_detector
from view.pages.security_guard.device_state import show_device_state
from view.pages.security_guard.issue_report import show_issue_report 

def show_security_dashboard():
    show_header()
    col1, col2 = st.columns([1,4])
    with col1:
        selected = get_security_selection()
    with col2:
        if selected == "Giám sát an ninh":
            show_security_detector()
        elif selected == "Trạng thái thiết bị":
            show_device_state()
        elif selected == "Báo cáo sự cố":
            show_issue_report()

