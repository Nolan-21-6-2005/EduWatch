import re

import streamlit as st

from src.frontend.camera_request import connect_camera
from src.database_query.buildings_manager import get_first_camera_id

# Tên hiển thị đầy đủ cho từng giảng đường (giá trị lưu trong session_state giữ nguyên).
BUILDING_NAMES = {
    "Giảng đường ND": "Giảng đường Nguyễn Đăng",
}

SESSION_MAP = {
    "Phòng thi": "exam",
    "Phòng thường": "study",
}

def _room_number(room: str) -> str:
    """ND102 -> 102 (nếu không có số thì trả nguyên chuỗi)."""
    match = re.search(r"\d+", room)
    return match.group() if match else room


main_col, log_col = st.columns([2.15, 1], gap="small")

<<<<<<< HEAD
    with main_col:
        # Hàng trên cùng: tab loại phòng (bên trái) + chọn giảng đường / phòng (bên phải).
        with st.container(key="detector_filters"):
            tab_col, building_col, room_col = st.columns(
                [1.5, 1, 0.7], gap="small", vertical_alignment="center"
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

            with building_col:
                building = st.selectbox(
                    "Giảng đường",
                    ("Giảng đường ND", "Giảng đường A", "Giảng đường B"),
                    key="building",
                    format_func=lambda name: BUILDING_NAMES.get(name, name),
                    label_visibility="collapsed",
                )

            with room_col:
                room = st.selectbox(
                    "Phòng",
                    ("ND101", "ND102"),
                    key="room",
                    label_visibility="collapsed",
                )
        session = SESSION_MAP[room_type]

        room_no = _room_number(room)

        building_label = BUILDING_NAMES.get(building, building)
        camera_id = get_first_camera_id(building_label, f"P.{room_no}")

        # Camera iframe dùng camera_id của phòng được chọn để violation log ghi đúng vị trí.
        connect_camera(
            building_label=building_label,
            room_label=f"Phòng {room_no}",
            room_short=f"P.{room_no}",
            camera_id=camera_id,
            session=session,
=======
with main_col:
    # Hàng trên cùng: tab loại phòng (bên trái) + chọn giảng đường / phòng (bên phải).
    with st.container(key="detector_filters"):
        tab_col, building_col, room_col = st.columns(
            [1.5, 1, 0.7], gap="small", vertical_alignment="center"
>>>>>>> 81d7401 (update)
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

        with building_col:
            building = st.selectbox(
                "Giảng đường",
                ("Giảng đường ND", "Giảng đường A", "Giảng đường B"),
                key="building",
                format_func=lambda name: BUILDING_NAMES.get(name, name),
                label_visibility="collapsed",
            )

        with room_col:
            room = st.selectbox(
                "Phòng",
                ("ND101", "ND102"),
                key="room",
                label_visibility="collapsed",
            )
    session = SESSION_MAP[room_type]

    room_no = _room_number(room)

    building_label = BUILDING_NAMES.get(building, building)
    camera_id = get_first_camera_id(building_label, f"P.{room_no}")

    # Camera iframe dùng camera_id của phòng được chọn để violation log ghi đúng vị trí.
    connect_camera(
        building_label=building_label,
        room_label=f"Phòng {room_no}",
        room_short=f"P.{room_no}",
        camera_id=camera_id,
        session=session,
    )

with log_col:
    # Nhật ký vi phạm tiếp tục là iframe riêng lấy dữ liệu từ FastAPI/SQLite.
    with st.container(key="log_list"):
        st.iframe(
            "http://localhost:8000/violations/panel",
            height=850
        )
