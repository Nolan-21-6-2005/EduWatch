import streamlit as st

from src.database_query.buildings_manager import get_buildings, get_cameras, get_rooms
from view.component.admin_table import render_admin_table

st.set_page_config(layout="wide", page_title="Quản lý tòa nhà")


def show_buildings():
    st.markdown(
        """
        <div class="page-header">
            <div>
                <h1 class="page-header-title">Danh sách tòa nhà</h1>
                <p class="page-header-subtitle">Quản lý tòa nhà, phòng học và số lượng camera theo dữ liệu hiện có.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    building_rows = []
    for building in get_buildings():
        rooms = get_rooms(building[0])
        camera_count = sum(len(get_cameras(room[0])) for room in rooms)
        building_rows.append(
            {
                "id": building[0],
                "name": building[1],
                "rooms": len(rooms),
                "cameras": camera_count,
                "status": 1,
            }
        )

    render_admin_table("buildings", building_rows, height=620)
