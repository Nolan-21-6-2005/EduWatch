import streamlit as st
from streamlit_searchbox import st_searchbox


PAGES = [
    ("Thống kê báo cáo", "view/pages/admin/statistic_report.py"),
    ("Giám sát trực tiếp", "view/pages/detector.py"),
    ("Nhật ký vi phạm", "view/pages/logs.py"),
    ("Danh sách tòa nhà", "view/pages/admin/buildings_management.py"),
    ("Quản lý người dùng", "view/pages/admin/user_management.py"),
    ("Thông tin cá nhân", "view/pages/profile.py"),
]


def search_pages(searchterm: str):
    if not searchterm:
        return []

    keyword = searchterm.lower().strip()

    return [
        (label, path)
        for label, path in PAGES
        if keyword in label.lower()
    ]


def navigate_to_page(selected):
    if selected:
        st.session_state["search_target_page"] = selected


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
        st_searchbox(
            search_pages,
            placeholder="Tìm kiếm trang",
            clear_on_submit=True,
            submit_function=navigate_to_page,
            key="topbar_search",

            style_overrides={
                "wrapper": {
                    "backgroundColor": "#ffffff",
                    "padding": 0,
                    "margin": 0,
                },

                "dropdown": {
                    "width": 0,
                    "height": 0,
                },

                "clear": {
                    "width": 16,
                    "height": 16,
                },

                "searchbox": {
                    "control": {
                        "minHeight": "40px",
                        "height": "40px",
                        "backgroundColor": "#ffffff",
                        "border": "1px solid #d9e2ea",
                        "borderRadius": "20px",
                        "boxShadow": "0 4px 10px rgba(24,33,47,0.06)",

                        "&:hover": {
                            "border": "1px solid #d9e2ea",
                        },

                        "&:focus-within": {
                            "border": "1px solid #20a85d",
                            "boxShadow": "0 0 0 3px rgba(32,168,93,0.14)",
                        },
                    },

                    "placeholder": {
                        "color": "#8a96a3",
                    },

                    "input": {
                        "color": "#1f2937",
                    },

                    "singleValue": {
                        "color": "#1f2937",
                    },

                    "menuList": {
                        "backgroundColor": "#ffffff",
                        "marginTop": "-8px",
                        "paddingTop": "6px",
                        "paddingBottom": "6px",
                        "borderRadius": "10px",
                        "boxShadow": "0 8px 24px rgba(24,33,47,0.12)",
                        "maxHeight": "320px",
                    },

                    "option": {
                        "color": "#334155",
                        "backgroundColor": "#ffffff",
                        "padding": "10px 14px",
                        "fontSize": "13px",
                        "borderRadius": "10px",
                        "highlightColor": "#20a85d",
                    },
                },
            },
        )

        # Chỉ chuyển trang sau khi searchbox đã xử lý submit
        target_page = st.session_state.pop(
            "search_target_page",
            None,
        )

        if target_page:
            st.switch_page(target_page)

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
