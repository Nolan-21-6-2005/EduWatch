import html as html_lib
from pathlib import Path
import requests
import streamlit as st
from utils.helper import load_file

IFRAME_HEIGHT = 910
_ASSET_DIR = Path(__file__).resolve().parents[2] / "view" / "asset"
_STYLE_DIR = Path(__file__).resolve().parents[2] / "view" / "style"
_CAMERA_HTML = (_ASSET_DIR / "camera.html").read_text(encoding="utf-8")
_CAMERA_JS = (_ASSET_DIR / "camera.js").read_text(encoding="utf-8")
_CAMERA_CSS = (_STYLE_DIR / "camera.css").read_text(encoding="utf-8")

def _camera_tile(cam):
    name = html_lib.escape(cam["name"])
    idle = cam["status"] == "idle"
    class_name = "camera-box idle" if idle else "camera-box"
    badge = '<span class="camera-status idle">NGHỈ</span>' if idle else '<span class="camera-status live">TRỰC TIẾP</span>'
    note = f'<div class="camera-idle-note">{html_lib.escape(cam["idle_text"])}</div>' if idle else ""
    stats = f'<div class="camera-stats"><div>FPS: {cam["fps"]}</div><div>Độ trễ: {cam["latency"]}ms</div></div>' if not idle else ""
    return f'''<div class="{class_name}">
      <div class="camera-badges"><span class="camera-label">{name}</span>{badge}</div>
      <div class="camera-toolbar"><button class="camera-btn" onclick="toggleCamera(this)" aria-label="Phóng to">↗</button></div>
      <img src="{cam["src"]}" onclick="selectCamera(this.closest('.camera-box'))" alt="{name}">
      {note}{stats}
    </div>'''

def connect_camera(
    building_label = "Giảng đường Nguyễn Đăng", 
    room_label = "Phòng 102", 
    room_short = "P.102", 
    camera_id: int = None, 
    session: str | None = None,
    role = 0
):
    params = []

    if camera_id is not None:
        params.append(f"camera_id={int(camera_id)}")

    if session:
        params.append(f"session={session}")

    live_src = "http://localhost:8000/video"

    if params:
        live_src += "?" + "&".join(params)

    img_src = "https://images.unsplash.com/photo-1557597774-9d273605dfa9?w=900"
    
    cameras = [
        {"name":"Cam 01 - Dãy trước","src":live_src,"status":"live","fps":30,"latency":12},
        {"name":"Cam 02 - Góc sau","src":img_src,"status":"live","fps":30,"latency":11},
        {"name":"Cam 03 - Từ trên cao","src":img_src,"status":"idle","idle_text":"CAM 03: KHÔNG PHÁT HIỆN CHUYỂN ĐỘNG"},
        {"name":"Cam 04 - Khu vực bục giảng","src":img_src,"status":"live","fps":30,"latency":14},
    ]
    
    tiles = "".join(_camera_tile(cam) for cam in cameras)

    replacements = {
        "__CAMERA_CSS__": _CAMERA_CSS,
        "__TILES__": tiles,
        "__CAMERA_JS__": _CAMERA_JS.replace("__TOGGLE_CAMERA__", load_file("src/frontend/toggle_camera.js")),
    }

    html = _CAMERA_HTML
    for key, value in replacements.items():
        html = html.replace(key, value)
    st.iframe(html, height=IFRAME_HEIGHT)

def start_camera():
    if "camera_running" not in st.session_state:
        st.session_state.camera_running = False
    st.session_state.camera_running = not st.session_state.camera_running
    requests.post("http://localhost:8000/start" if st.session_state.camera_running else "http://localhost:8000/stop")

def activate_camera(model_active):
    st.session_state.last_model_state = model_active
    requests.post("http://localhost:8000/model/start" if model_active else "http://localhost:8000/model/stop")
