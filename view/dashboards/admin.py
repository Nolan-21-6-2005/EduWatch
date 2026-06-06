import streamlit as st
from view.component.sidebar.admin import get_selection
from view.component.header import show_header
from view.pages.detector import show_detector
from view.pages.logs import show_logs
from view.pages.admin.statistic_report import show_report 
from view.pages.admin.user_management import show_user
from view.pages.admin.buildings_management import show_buildings

def show_admin_dashboard():
    show_header()
    col1, col2 = st.columns([1,4])
    with col1:
        selected = get_selection()
    with col2:
        if selected == "Thống kê báo cáo":
            show_report()
        elif selected == "Giám sát trực tiếp":
            show_detector()
        elif selected == "Nhật ký vi phạm":
            show_logs()
        elif selected == "Danh sách tòa nhà":
            show_buildings()
        elif selected == "Quản lý người dùng":
            show_user()



