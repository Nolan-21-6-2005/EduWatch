import streamlit as st
from streamlit_navigation_bar import st_navbar

def show_topbar():
    """Hiển thị topbar tùy biến theo giao diện EduWatch."""
    
    st.markdown('<div class="ew-topbar-spacer"></div>', unsafe_allow_html=True)
    with st.container(key="ew_topbar"):
        left, overview, analysis, bell, settings = st.columns(
            [4.8, 1.05, 1.05, 0.55, 0.55],
            vertical_alignment="center",
            gap="small",
        )

        with left:
            st.text_input(
                "Tìm kiếm",
                placeholder="Tòa nhà, Phòng học...",
                label_visibility="collapsed",
                key="topbar_search",
            )

        with overview:
            st.button("Tổng quan", key="topbar_overview", type="tertiary", width="stretch")

        with analysis:
            st.button("Phân tích", key="topbar_analysis", type="tertiary", width="stretch")

        with bell:
            st.button(":material/notifications:", key="topbar_notifications", type="tertiary", help="Thông báo")

        with settings:
            st.button(":material/settings:", key="topbar_settings", type="tertiary", help="Cài đặt")
