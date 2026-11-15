import streamlit as st
from streamlit_extras.avatar import avatar
from utils.config import AVATAR_DIR
ROLE_NAMES = {
    0: "Học viện",
    1: "Giảng viên",
    2: "Bảo vệ",
}


def show_footer():
    """Hiển thị khu vực tài khoản ở cuối sidebar theo phong cách Medcare."""
    with st.sidebar:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        with st.container(key="ew_sidebar_footer"):
            if avatar(
                str(AVATAR_DIR / "default.png"),
                label=st.session_state.get("professor_id", ""),
                caption=ROLE_NAMES.get(st.session_state.get("role"), "Người dùng"),
                on_click="rerun",
                key="clickable_avatar",
            ):
                st.switch_page("view/pages/profile.py")

            if st.button(":material/logout:  Đăng xuất", width="stretch"):
                st.session_state["professor_id"] = ""
                st.session_state["role"] = ""
                st.rerun()
