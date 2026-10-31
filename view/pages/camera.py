import re

import streamlit as st

from src.frontend.camera_request import connect_camera
from src.database_query.buildings_manager import get_first_camera_id
from utils.config import BUILDING_NAMES, SESSION_MAP
from utils.helper import _room_number 



def display_camera():
    col_main_cam, col_right_status = st.columns([3, 1], gap="medium")

    with col_main_cam:
        # Hàng trên cùng: tab loại phòng (bên trái) + chọn giảng đường / phòng (bên phải).
        with st.container(key="detector_filters"):
            building_col, room_col = st.columns(
                2, gap="small", vertical_alignment="center"
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

        room_no = _room_number(room)

        building_label = BUILDING_NAMES.get(building, building)
        camera_id = get_first_camera_id(building_label, f"P.{room_no}")

        # Camera iframe dùng camera_id của phòng được chọn để violation log ghi đúng vị trí.
        connect_camera(
            building_label=building_label,
            room_label=f"Phòng {room_no}",
            room_short=f"P.{room_no}",
            camera_id=camera_id,
            role = 0
        )
    with col_right_status:
        st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
        st.markdown(
        """
        <div class="status-panel">
            <div class="status-panel-title">TRẠNG THÁI CAMERA</div>
            <div class="status-row"><span class="status-name">Bàn giáo viên</span><span class="badge-pill pill-active">Hoạt động</span></div>
            <div class="status-row"><span class="status-name">Cuối lớp</span><span class="badge-pill pill-active">Hoạt động</span></div>
            <div class="status-row"><span class="status-name">Cửa chính</span><span class="badge-pill pill-active">Hoạt động</span></div>
            <div class="status-row"><span class="status-name">Cửa phụ</span><span class="badge-pill pill-error">Mất kết nối</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )