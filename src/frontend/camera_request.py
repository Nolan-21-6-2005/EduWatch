import html as html_lib
import base64
from pathlib import Path
import streamlit as st

from utils.config import API_BASE

# Chiều cao dự phòng của iframe; chiều cao thật do CSS --ew-stage-h (detector.css) quyết định.
IFRAME_HEIGHT = 820
_ASSET_DIR = Path(__file__).resolve().parents[2] / "view" / "asset"
_STYLE_DIR = Path(__file__).resolve().parents[2] / "view" / "style"
_CAMERA_HTML = (_ASSET_DIR / "camera.html").read_text(encoding="utf-8")
_CAMERA_JS = (_ASSET_DIR / "camera.js").read_text(encoding="utf-8")
_CAMERA_CSS = (_STYLE_DIR / "camera.css").read_text(encoding="utf-8")
_TOGGLE_CAMERA_JS = (_ASSET_DIR / "toggle_camera.js").read_text(encoding="utf-8")
_PLACEHOLDER_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">'
    '<rect width="640" height="360" fill="#dce5df"/>'
    '<path d="M270 145h100l20 24h45v76H225v-76h25z" fill="#a8b8ad"/>'
    '<circle cx="320" cy="207" r="30" fill="#eaf0ec" stroke="#718579" stroke-width="8"/>'
    '<text x="320" y="290" text-anchor="middle" font-family="sans-serif" font-size="20" fill="#52675a">CHƯA CÓ ẢNH</text>'
    '</svg>'
)
_PLACEHOLDER_SRC = "data:image/svg+xml;base64," + base64.b64encode(
    _PLACEHOLDER_SVG.encode("utf-8")
).decode("ascii")

ICON_EXPAND = '<svg class="ico-expand" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4h6v6M10 20H4v-6M20 4l-7 7M4 20l7-7"/></svg>'
ICON_FULL = '<svg class="ico-full" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>'

def _camera_tile(cam, index, room_short):
    """Một khung camera. Ảnh và trạng thái (đang tải / đã có ảnh / chưa có ảnh / lỗi) do camera.js cập nhật."""
    name = html_lib.escape(cam["name"])
    src = html_lib.escape(cam["src"], quote=True)
    state = html_lib.escape(cam["status"], quote=True)
    idle_text = html_lib.escape(cam.get("idle_text", ""))
    code = html_lib.escape(f"{room_short} - Cam {index:02d}")
    frame_url = html_lib.escape(cam["frame_url"], quote=True)
    upload_url = html_lib.escape(cam["upload_url"], quote=True)
    return f'''<div class="camera-box" data-name="{name}" data-state="{state}" data-idle-text="{idle_text}"
         data-frame-url="{frame_url}" data-upload-url="{upload_url}"
         title="Nhấp hoặc kéo thả ảnh vào đây để tải lên" onclick="pickImage(this, event)">
      <input type="file" class="cam-file" accept="image/*" hidden>
      <img src="{src}" alt="{name}" crossorigin="anonymous">
      <div class="cam-note"></div>
      <div class="cam-top">
        <span class="cam-name">{name}</span>
        <span class="cam-status" data-status></span>
        <button class="cam-expand" onclick="onExpand(event, this)" aria-label="Phóng to">{ICON_EXPAND}{ICON_FULL}</button>
      </div>
      <span class="cam-code">{code}</span>
      <div class="cam-stats"></div>
      <div class="cam-foot"><span>{name}</span><span class="cam-status" data-status></span></div>
    </div>'''


# Tên hiển thị của 4 khung, theo thứ tự camera của phòng (khung i -> camera thứ i).
_TILE_NAMES = (
    "Cam 01 - Cửa chính",
    "Cam 02 - Bàn giáo viên",
    "Cam 03 - Cuối lớp",
    "Cam 04 - Cửa phụ",
)


def connect_camera(
    *,
    room_short: str,
    camera_ids: list[int],
    role: int,
    session: str = "study",
):
    """Hiển thị 4 khung camera; mỗi khung nhận ảnh tải lên thay cho luồng webcam.

    Khung i gắn với camera thứ i của phòng (thiếu thì dùng camera đầu tiên) để vi phạm
    được ghi đúng phòng. Ảnh được lưu phía backend nên không mất khi giao diện tải lại.
    """
    if not camera_ids:
        raise ValueError("camera_ids không được rỗng")

    cameras = []
    for slot, name in enumerate(_TILE_NAMES, 1):
        camera_id = camera_ids[slot - 1] if slot <= len(camera_ids) else camera_ids[0]
        query = f"camera_id={int(camera_id)}&slot={slot}"
        cameras.append({
            "name": name,
            "src": _PLACEHOLDER_SRC,
            "status": "connecting",
            "idle_text": "Nhấp để tải ảnh lên",
            "frame_url": f"{API_BASE}/camera/frame?{query}&session={session}",
            "upload_url": f"{API_BASE}/camera/upload?{query}",
        })

    tiles = "".join(_camera_tile(cam, i, room_short) for i, cam in enumerate(cameras, 1))

    replacements = {
        "__CAMERA_CSS__": _CAMERA_CSS,
        "__TILES__": tiles,
        "__CAMERA_JS__": _CAMERA_JS.replace("__TOGGLE_CAMERA__", _TOGGLE_CAMERA_JS),
        "__API_BASE__": API_BASE,  # cuối cùng: thay cả trong JS vừa chèn
    }

    html = _CAMERA_HTML
    for key, value in replacements.items():
        html = html.replace(key, value)
    st.iframe(html, height=IFRAME_HEIGHT)
