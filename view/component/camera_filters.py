"""Shared database-backed building and room selectors for camera pages."""

import streamlit as st

from src.database_query.buildings_manager import get_buildings, get_rooms
from utils.config import BUILDING_NAMES


def render_camera_location_filters(building_col, room_col, *, key_prefix: str):
    buildings = get_buildings(include_deleted=False)
    if not buildings:
        st.warning("Chưa có tòa nhà đang hoạt động trong cơ sở dữ liệu.")
        return None, None

    building_by_name = {item["ten_toa"]: item for item in buildings}
    building_names = list(building_by_name)

    with building_col:
        selected_building_name = st.selectbox(
            "Giảng đường",
            options=building_names,
            format_func=lambda value: BUILDING_NAMES.get(value, value),
            key=f"{key_prefix}_building",
            label_visibility="collapsed",
        )

    selected_building = building_by_name[selected_building_name]
    rooms = get_rooms(int(selected_building["id"]), include_deleted=False)
    if not rooms:
        with room_col:
            st.caption("Chưa có phòng hoạt động")
        return selected_building, None

    room_by_name = {item["ten_phong"]: item for item in rooms}
    with room_col:
        selected_room_name = st.selectbox(
            "Phòng",
            options=list(room_by_name),
            key=f"{key_prefix}_room_{selected_building['id']}",
            label_visibility="collapsed",
        )

    return selected_building, room_by_name[selected_room_name]
