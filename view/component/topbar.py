import streamlit as st
from streamlit_searchbox import st_searchbox


def search_wikipedia(searchterm: str) -> list:
    # TODO: thay bằng hàm tìm tòa nhà/phòng học thật thay vì Wikipedia.
    return wikipedia.search(searchterm) if searchterm else []


def show_topbar():
    st.markdown(
        '<div class="ew-topbar-spacer"></div>',
        unsafe_allow_html=True,
    )

    with st.container(
        key="ew_topbar",
        horizontal=True,
        vertical_alignment="center",
        gap="small",
    ):
        selected_value = st_searchbox(
            search_wikipedia,
            placeholder="Tòa nhà, Phòng học...",
            key="topbar_search",
            # Component này chạy trong iframe riêng nên CSS của trang không
            # len vào được — toàn bộ giao diện BÊN TRONG ô search (nền, bo
            # góc, màu chữ, và xóa mũi tên dropdown) phải khai báo ở đây.
            style_overrides={
                # width/height = 0 để ẩn hẳn mũi tên dropdown bên phải ô.
                "dropdown": {"width": 0, "height": 0},
                "searchbox": {
                    "control": {
                        "minHeight": "40px",
                        "height": "40px",
                        "backgroundColor": "#ffffff",
                        "border": "1.5px solid #d9e2ea",
                        "borderRadius": "20px",
                        "boxShadow": "0 1px 4px rgba(24,33,47,0.06)",
                    },
                    "placeholder": {"color": "#8a96a3"},
                    "input": {"color": "#1f2937"},
                    "singleValue": {"color": "#1f2937"},
                },
            },
        )

        st.button(
            "●  System Online",
            key="topbar_system",
            type="primary",
        )

        st.button(
            ":material/notifications:",
            key="topbar_notifications",
            type="tertiary",
            help="Thông báo",
        )

        st.button(
            ":material/settings:",
            key="topbar_settings",
            type="tertiary",
            help="Cài đặt",
        )
