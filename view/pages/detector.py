import streamlit as st
from src.frontend.camera_request import (
    connect_camera,
    start_camera,
    activate_camera,
    get_message
)
import requests
from helper.script_loader import load_file

# Đọc file CSS của Camera Panel (Thêm encoding='utf-8' để tránh lỗi font)
css = load_file("view/style/style.css")

st.set_page_config(layout="wide", page_title="Giám sát trực tiếp")

def show_detector():
    backdground_color = st.get_option("theme.backgroundColor")
    
    st.markdown(f"""
        <style>
            {css}
        </style>
    """, unsafe_allow_html=True)
    st.write("")

    # =========================
    # MAIN LAYOUT
    # =========================
    main_col1, main_col2 = st.columns([2, 1])
    
    # =========================
    # HANDLE EVENTS
    # =========================
    with main_col1:
        st.subheader("Giám sát trực tiếp")

        connect_camera()

        with st.container(border = True):
            col1, col2 = st.columns([1, 1])
            with col1:
                btn = st.button("Start Camera")
            with col2:
                model_active = st.toggle(
                    "Detector",
                    label_visibility="hidden"
                )  
            activate_camera(model_active)
    
    with main_col2:
        with st.container(border=True):
            st.subheader("NHẬT KÝ VI PHẠM")
            get_message()
    if btn:
        start_camera()
        st.rerun()
