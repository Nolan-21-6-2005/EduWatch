import streamlit as st
import requests
from helper.script_loader import load_file

css_code = load_file("view/style/style.css")
js_code = load_file("src/frontend/script.js")

def connect_camera():
    # Định nghĩa link luồng live và các ảnh placeholder trực tiếp bằng link sạch (.jpg)
    live_src = "http://localhost:8000/video"
    img_src = "https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=500"

    st.components.v1.html(f"""
        <style>
            {css_code}
        </style>
        <div class="camera-grid">
            <div class="camera-box">
                <span class="camera-label">Camera Chính (Live)</span>
                <img src="{live_src}">
            </div>
            
            <div class="camera-box">
                <span class="camera-label">Camera Phụ 1</span>
                <img src="{img_src}">
            </div>
            
            <div class="camera-box">
                <span class="camera-label">Camera Phụ 2</span>
                <img src="{img_src}">
            </div>
            
            <div class="camera-box">
                <span class="camera-label">Camera Phụ 3</span>
                <img src="{img_src}">
            </div>
        </div>
    """, height=600) # Chiều cao tổng cho cả khối 2x2 (khoảng 500px là vừa vặn lấp đầy)
    
def start_camera():
    if "camera_running" not in st.session_state:
        st.session_state.camera_running = False
    st.session_state.camera_running = (
        not st.session_state.camera_running)

    if st.session_state.camera_running:
        requests.post("http://localhost:8000/start")
    else:
        requests.post("http://localhost:8000/stop") 

def activate_camera(model_active):
    st.session_state.last_model_state = (model_active)

    if model_active:
        requests.post("http://localhost:8000/model/start")
    else:
        requests.post("http://localhost:8000/model/stop")

def get_message():
    st.components.v1.html(
        f"""
        <div id="alerts"></div>
        <script>
            {js_code}
        </script>
        """, height = 600)


