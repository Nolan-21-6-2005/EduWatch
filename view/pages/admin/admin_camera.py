import streamlit as st

from view.pages.camera import display_camera

st.set_page_config(
    page_title="Giám sát trực tiếp",
    layout="wide",
    initial_sidebar_state="expanded",
)

display_camera()