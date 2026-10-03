"""
File này chỉ lo việc điều hướng.
Nội dung từng trang vẫn nằm trong view/pages/.
"""

import streamlit as st

# Trang đăng nhập/đăng ký.
SIGN_IN_PAGE = st.Page(
    "view/pages/auth/sign_in.py",
    title="Đăng nhập",
    icon=":material/login:",
    url_path="login",
    default=True,
)

SIGN_UP_PAGE = st.Page(
    "view/pages/auth/sign_up.py",
    title="Đăng ký",
    icon=":material/how_to_reg:",
    url_path="signup",
)

PROFILE_PAGE = st.Page(
    "view/pages/profile.py",
    title="Trang cá nhân",
    url_path="profile",
    visibility="hidden"
)

def get_pages_for_role(role: int):
    """Trả về danh sách trang Dashboard tương ứng với role."""

    if role == 0:
        return [
            st.Page(
                "view/pages/admin/statistic_report.py",
                title="Thống kê báo cáo",
                icon=":material/bar_chart:",
                url_path="statistics",
            ),
            st.Page(
                "view/pages/detector.py",
                title="Giám sát trực tiếp",
                icon=":material/videocam:",
                url_path="monitoring",
            ),
            st.Page(
                "view/pages/logs.py",
                title="Nhật ký vi phạm",
                icon=":material/menu_book:",
                url_path="logs",
            ),
            st.Page(
                "view/pages/admin/buildings_management.py",
                title="Danh sách tòa nhà",
                icon=":material/apartment:",
                url_path="buildings",
            ),
            st.Page(
                "view/pages/admin/user_management.py",
                title="Quản lý người dùng",
                icon=":material/group:",
                url_path="users",
            ),
            PROFILE_PAGE,
        ]

    if role == 1:
        return [
            st.Page(
                "view/pages/detector.py",
                title="Giám sát trực tiếp",
                icon=":material/videocam:",
                url_path="monitoring",
            ),
            st.Page(
                "view/pages/logs.py",
                title="Nhật ký vi phạm",
                icon=":material/menu_book:",
                url_path="logs",
            ),
            st.Page(
                "view/pages/supervision/field_report.py",
                title="Xuất biên bản",
                icon=":material/description:",
                url_path="field-report",
            ),
            PROFILE_PAGE,
        ]

    if role == 2:
        return [
            st.Page(
                "view/pages/security_guard/security_detector.py",
                title="Giám sát an ninh",
                icon=":material/shield:",
                url_path="security-monitoring",
            ),
            st.Page(
                "view/pages/security_guard/device_state.py",
                title="Trạng thái thiết bị",
                icon=":material/devices:",
                url_path="device-state",
            ),
            st.Page(
                "view/pages/security_guard/issue_report.py",
                title="Báo cáo sự cố",
                icon=":material/report_problem:",
                url_path="issue-report",
            ),
            PROFILE_PAGE,
        ]

    return []
