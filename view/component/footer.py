import streamlit as st
from streamlit_extras.avatar import avatar

ROLE_NAMES = {
    0: "Quản trị viên",
    1: "Giám sát",
    2: "An ninh",
}


def show_footer():
    """Hiển thị khu vực tài khoản ở cuối sidebar theo phong cách Medcare."""
    with st.sidebar:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.divider()

        user_col, action_col = st.columns([3.2, 1], gap="small")
        with user_col:
            avatar(
                "https://avatars.githubusercontent.com/u/1673013?v=4",
                label=st.session_state.get("professor_id", ""),
                caption=ROLE_NAMES.get(st.session_state.get("role"), "Người dùng"),
                on_click="rerun",
                key="clickable_avatar",
            )
        with action_col:
            st.button(
                ":material/notifications:",
                key="notification",
                type="tertiary",
                help="Thông báo",
            )

        if st.button(":material/logout:  Đăng xuất", width="stretch"):
            st.session_state["professor_id"] = ""
            st.session_state["role"] = ""
            st.rerun()
