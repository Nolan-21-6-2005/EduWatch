import streamlit as st

from view.pages.camera import display_camera

st.set_page_config(
    layout="wide", 
    page_title="EduWatch VNUA - Bảo vệ",
    initial_sidebar_state="expanded",
)

display_camera()