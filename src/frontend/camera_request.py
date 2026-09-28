import html as html_lib
from pathlib import Path
import requests
import streamlit as st
from helper.script_loader import load_file

IFRAME_HEIGHT = 910
_ASSET_DIR = Path(__file__).resolve().parents[2] / "view" / "asset"
_STYLE_DIR = Path(__file__).resolve().parents[2] / "view" / "style"
_CAMERA_HTML = (_ASSET_DIR / "camera.html").read_text(encoding="utf-8")
_CAMERA_JS = (_ASSET_DIR / "camera.js").read_text(encoding="utf-8")
_CAMERA_CSS = (_STYLE_DIR / "camera.css").read_text(encoding="utf-8")

ICON_GRID = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M3 3h8v8H3V3zm10 0h8v8h-8V3zM3 13h8v8H3v-8zm10 0h8v8h-8v-8z"/></svg>'
ICON_CAMERA = '<svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M9 3 7.2 5H4a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-3.2L15 3H9zm3 12a5 5 0 1 1 0-10 5 5 0 0 1 0 10z"/></svg>'
ICON_AI = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3"/></svg>'

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

def connect_camera(building_label="Giảng đường Nguyễn Đăng", room_label="Phòng 102", room_short="P.102", camera_id=None):
    live_src = "http://localhost:8000/video" + (f"?camera_id={int(camera_id)}" if camera_id else "")
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
        "__BUILDING__": html_lib.escape(building_label),
        "__ROOM__": html_lib.escape(room_label),
        "__TITLE__": html_lib.escape(f"{building_label} - {room_short}"),
        "__ICON_GRID__": ICON_GRID,
        "__ICON_CAMERA__": ICON_CAMERA,
        "__ICON_AI__": ICON_AI,
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
