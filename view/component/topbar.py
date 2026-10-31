import streamlit as st
from streamlit_searchbox import st_searchbox
from view.component.notification import notification_bell, notification_panel

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


def show_topbar(page_title="Trang chủ"):
    st.markdown(
        '<div class="ew-topbar-spacer"></div>',
        unsafe_allow_html=True,
    )

    with st.container(
        key="ew_topbar",
        horizontal=True,
        vertical_alignment="center",
    ):
        st.markdown(
            f"""
            <div class="ew-breadcrumb">
                <span class="ew-breadcrumb-home">EduWatch</span>
                <span class="ew-breadcrumb-separator">/</span>
                <span class="ew-breadcrumb-current">{page_title}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st_searchbox(
            search_pages,
            placeholder="Tìm kiếm trang",
            clear_on_submit=True,
            submit_function=navigate_to_page,
            key="topbar_search",

            style_overrides={
                "wrapper": {
                    "backgroundColor": "#f0f3f1",
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
                        "minHeight": "42px",
                        "height": "42px",
                        "backgroundColor": "#ffffff",
                        "border": "1px solid #d5dad7",
                        "borderRadius": "16px",
                        "boxShadow": "none",

                        "&:hover": {
                            "border": "1px solid #cdd3cf",
                        },

                        "&:focus-within": {
                            "backgroundColor": "#e8ebe9",
                            "border": "1px solid #9acbaa",
                            "boxShadow": "0 0 0 3px rgba(76, 166, 107,0.10)",
                        },
                    },

                    "placeholder": {
                        "color": "#77857c",
                    },

                    "input": {
                        "color": "#24382c",
                    },

                    "singleValue": {
                        "color": "#24382c",
                    },

                    "menuList": {
                        "backgroundColor": "#ffffff",
                        "marginTop": "-8px",
                        "paddingTop": "6px",
                        "paddingBottom": "6px",
                        "borderRadius": "10px",
                        "boxShadow": "0 8px 24px rgba(25, 59, 38,0.12)",
                        "maxHeight": "320px",
                    },

                    "option": {
                        "color": "#3d4a40",
                        "backgroundColor": "#ffffff",
                        "padding": "10px 14px",
                        "fontSize": "13px",
                        "borderRadius": "10px",
                        "highlightColor": "#4ca66b",
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

        st.html('<span class="ew-status ok">System Online</span>')

        notification_bell()    
            
        st.button(
            ":material/settings:",
            key="topbar_settings",
            help="Cài đặt",
        )
        
    notification_panel() 
