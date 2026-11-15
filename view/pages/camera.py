import streamlit as st
from html import escape

from src.frontend.camera_request import connect_camera
from src.database_query.buildings_manager import get_cameras, get_room_camera_ids
from utils.helper import _room_number
from view.component.camera_filters import render_camera_location_filters


def display_camera(role: int):
    col_main_cam, col_right_status = st.columns([3, 1], gap="medium")

    with col_main_cam:
        with st.container(key="detector_filters"):
            building_col, room_col = st.columns(
                2, gap="small", vertical_alignment="center"
            )
            selected_building, selected_room = render_camera_location_filters(
                building_col, room_col, key_prefix="camera_page"
            )

        if selected_building is None or selected_room is None:
            st.info("Chọn một tòa nhà và phòng đang hoạt động để xem camera.")
            return

        building_name = selected_building["ten_toa"]
        room_name = selected_room["ten_phong"]
        room_no = _room_number(room_name)
        camera_ids = get_room_camera_ids(building_name, room_name)
        if not camera_ids:
            st.warning("Phòng này chưa có camera đang hoạt động trong cơ sở dữ liệu.")
        else:
            # cam_stage: chiều cao iframe do CSS (--ew-stage-h trong detector.css) quyết định,
            # để 4 khung camera vừa gọn một màn hình.
            with st.container(key="cam_stage"):
                connect_camera(
                    room_short=f"P.{room_no}",
                    camera_ids=camera_ids,
                    role=role,
                )

    with col_right_status:
        cameras = get_cameras(int(selected_room["id"]))
        status_rows = []
        for camera in cameras:
            active = int(camera.get("status") or 0) == 1
            status_label = "Được kích hoạt" if active else "Ngừng kích hoạt"
            status_class = "pill-active" if active else "pill-error"
            status_rows.append(
                f'<div class="status-row"><span class="status-name">'
                f'{escape(str(camera["vi_tri_goc"]))}</span><span class="badge-pill {status_class}">'
                f'{status_label}</span></div>'
            )

        st.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
        rows_html = "".join(status_rows) or (
            '<div class="status-row"><span class="status-name">'
            'Chưa khai báo camera</span></div>'
        )
        st.markdown(
            '<div class="status-panel">'
            '<div class="status-panel-title">CẤU HÌNH CAMERA</div>'
            f'{rows_html}'
            '</div>',
            unsafe_allow_html=True,
        )
