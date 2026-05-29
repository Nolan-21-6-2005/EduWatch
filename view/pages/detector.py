import streamlit as st
from src.frontend.camera_controller import (
    connect_camera,
    start_camera,
    activate_camera,
    get_message
)
from utils.load_css import apply_css

def show_detector():
    backdground_color = st.get_option("theme.backgroundColor")

    # =========================
    # HIDE SIDEBAR & LOAD GLOBAL CSS
    # =========================
    st.markdown("""
    <style>
    section[data-testid="stSidebar"] {
        width: 0px !impor tant;
        min-width: 0px !important;
    }

    section[data-testid="stSidebar"] > div {
      display: none !important;
    }

    button[kind="header"] {
      display: none !important;
    }
    <style>
    """, unsafe_allow_html=True)

    # Đọc file CSS của Camera Panel (Thêm encoding='utf-8' để tránh lỗi font)
    with open("view/style/detector_style.css", "r", encoding="utf-8") as f:
        camera_css = f.read()

    # =========================
    # REAL STREAMLIT WIDGETS
    # =========================
    with st.sidebar:
        current_model_state = st.session_state.get("last_model_state", False)
        st.checkbox(
            label="MODEL_TOGGLE_CONTROL",
            key="last_model_state",
            value=current_model_state,
            on_change=lambda: activate_camera(st.session_state.last_model_state)
        )
        btn_hidden = st.button(label="BTN_CAMERA_CONTROL", key="btn_hid")

    # =========================
    # HANDLE EVENTS
    # =========================
    if btn_hidden:
        start_camera()
        st.rerun()

    # =========================
    # MAIN LAYOUT
    # =========================
    main_col1, main_col2 = st.columns([2, 1])

    with main_col1:
        connect_camera()
        st.write("")
        is_cam_running = st.session_state.get("camera_running", False)
        is_model_active = st.session_state.get("last_model_state", False)
        
        # Định nghĩa màu sắc động cho Button dựa trên trạng thái camera
        btn_color = "#ff4b4b" if is_cam_running else "#2cbd6c"
        btn_label = "Stop Camera" if is_cam_running else "Start Camera"
        checkbox_checked = "checked" if is_model_active else ""

        # =========================
        # CUSTOM UI (HTML COMPONENT)
        # =========================
        st.components.v1.html(f"""
            <style>
            /* Nhúng toàn bộ nội dung file CSS đã đọc vào đây */
            {camera_css}
            
            /* Chỉ giữ lại các thuộc tính có biến Python động */
            .control-panel {{
                background: {backdground_color};
            }}
            .action-btn {{
                background-color: {btn_color};
                color: white;
                border: none;
                padding: 10px 22px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
            }}
            </style>
            
            <div class="control-panel">
                <button class="action-btn" onclick="clickStreamlitButton()">
                    {btn_label}
                </button>
                <div class="toggle-container">
                    <label class="switch">
                        <input type="checkbox" {checkbox_checked} onclick="clickStreamlitCheckbox(); event.stopPropagation();">
                        <span class="slider"></span>
                    </label>
                    <span>Activate Model</span>
                </div>
            </div>
            
            <script>
            function clickStreamlitButton() {{
                const buttons = window.parent.document.querySelectorAll("button");
                for (let btn of buttons) {{
                    if (btn.innerText && btn.innerText.includes("BTN_CAMERA_CONTROL")) {{
                        btn.click();
                        break;
                    }}
                }}
            }}

            function clickStreamlitCheckbox() {{
                const labels = window.parent.document.querySelectorAll("label");
                for (let label of labels) {{
                    if (label.innerText && label.innerText.includes("MODEL_TOGGLE_CONTROL")) {{
                        label.click();
                        break;
                    }}
                }}
            }}
            </script>
        """, height=90)

    with main_col2:
        st.subheader("NHẬT KÝ VI PHẠM")
        get_message()
