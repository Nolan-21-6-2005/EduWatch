import streamlit as st
import requests

with open("src/frontend/script.js") as f:
    js_code = f.read()

def connect_camera():
    # Định nghĩa link luồng live và các ảnh placeholder trực tiếp bằng link sạch (.jpg)
    live_src = "http://localhost:8000/video"
    img_src = "https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=500"

    st.components.v1.html(f"""
        <style>
            /* Chỉnh lại độ rộng và padding của vùng nội dung chính */
            [data-testid="stMain"] {{
                padding-left: 2rem;
                padding-right: 2rem;
            }}
            
            /* Tạo lưới 2x2 bằng CSS Grid */
            .camera-grid {{
                display: grid;
                grid-template-columns: repeat(2, 1fr); /* 2 cột bằng nhau */
                gap: 12px; /* Khoảng cách giữa các ô */
                width: 100%;
                box-sizing: border-box;
            }}
            
            /* Định dạng chung cho từng hộp camera */
            .camera-box {{
                position: relative;
                width: 100%;
                aspect-ratio: 4 / 3; /* Cố định tỷ lệ khung hình 4:3 cho cả 4 ô */
                background-color: #1e1e1e;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }}
            
            /* Ép ảnh/video phủ kín hộp */
            .camera-box img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            
            /* Nhãn đè lên góc camera cho chuyên nghiệp giống app camera thực tế */
            .camera-label {{
                position: absolute;
                top: 8px;
                left: 8px;
                background: rgba(0, 0, 0, 0.6);
                color: #fff;
                padding: 2px 8px;
                font-family: sans-serif;
                font-size: 12px;
                border-radius: 4px;
                pointer-events: none;
            }}
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
        """
    )


