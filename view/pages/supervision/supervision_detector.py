import streamlit as st
import requests

from src.frontend.camera_request import IFRAME_HEIGHT, connect_camera
from src.database_query.buildings_manager import get_first_camera_id
from view.component.camera_filters import render_camera_location_filters
from utils.config import SESSION_MAP
from utils.helper import _room_number

API_BASE = "http://localhost:8000"


def _set_ai_state():
    enabled = bool(st.session_state.get("supervision_ai", False))
    endpoint = "/model/start" if enabled else "/model/stop"
    try:
        response = requests.post(f"{API_BASE}{endpoint}", timeout=3)
        response.raise_for_status()
    except requests.RequestException as exc:
        st.session_state["supervision_ai_error"] = str(exc)


if "supervision_ai" not in st.session_state:
    try:
        status_response = requests.get(f"{API_BASE}/camera/status", timeout=3)
        status_response.raise_for_status()
        st.session_state["supervision_ai"] = bool(
            status_response.json().get("detector_active", False)
        )
    except requests.RequestException:
        st.session_state["supervision_ai"] = False

main_col, log_col = st.columns([3.2, 1.45], gap="small")

with main_col:
    # Hàng trên cùng: tab loại phòng (bên trái) + chọn giảng đường / phòng (bên phải).
    with st.container(key="detector_filters"):
        tab_col, building_col, room_col, ai_col = st.columns(
            [1.35, 1, 0.7, 0.65], gap="small", vertical_alignment="center"
        )

        with tab_col:
            room_type = st.segmented_control(
                "Loại phòng",
                ("Phòng thi", "Phòng thường"),
                default="Phòng thường",
                required=True,
                key="room_type",
                label_visibility="collapsed",
            )

        selected_building, selected_room = render_camera_location_filters(
            building_col, room_col, key_prefix="supervision_camera"
        )
        with ai_col:
            st.toggle(
                "AI",
                key="supervision_ai",
                help="Bật hoặc tắt nhận diện vi phạm cho phiên giám sát.",
                on_change=_set_ai_state,
            )
    if st.session_state.get("supervision_ai_error"):
        st.error(f"Không thể thay đổi trạng thái AI: {st.session_state.pop('supervision_ai_error')}")
    session = SESSION_MAP[room_type]

    if selected_building is None or selected_room is None:
        st.info("Chọn một tòa nhà và phòng đang hoạt động để xem camera.")
        st.stop()

    room_no = _room_number(selected_room["ten_phong"])
    building_label = selected_building["ten_toa"]
    camera_id = get_first_camera_id(building_label, selected_room["ten_phong"])
    if camera_id is None:
        st.warning("Phòng này chưa có camera đang hoạt động trong cơ sở dữ liệu.")
        st.stop()

    # Camera iframe dùng camera_id của phòng được chọn để violation log ghi đúng vị trí.
    # cam_stage: chiều cao iframe do CSS (--ew-stage-h trong detector.css) quyết định.
    with st.container(key="cam_stage"):
        connect_camera(
            room_short=f"P.{room_no}",
            camera_id=camera_id,
            session=session,
            role=1,
        )

with log_col:
    # Nhật ký vi phạm tiếp tục là iframe riêng lấy dữ liệu từ FastAPI/SQLite.
    with st.container(key="log_list"):
        st.iframe("http://localhost:8000/violations/panel", height=IFRAME_HEIGHT)
