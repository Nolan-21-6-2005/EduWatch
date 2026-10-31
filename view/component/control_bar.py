import streamlit as st

with st.container(key="camera-control-bar"):
    building_col, room_col, label_col, toggle_col = st.columns(
        3, gap="small", vertical_alignment="center"
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
    with label_col:
        <div class="detector-control">
        <div class="detector-copy">
            <div class="detector-label">TRÍ TUỆ NHÂN TẠO</div>
            <div id="detectorState" class="detector-state">Ngừng hoạt động</div>
        </div>
        <>

    <button id="detectorSwitch" class="detector-switch off" onclick="toggleDetector()" aria-label="Bật tắt detector">
        <span class="detector-knob">__ICON_AI__</span>
    </button>