"""Khai báo các trang của ứng dụng.

File này chỉ lo việc điều hướng.
Nội dung từng trang vẫn nằm trong view/pages/.
"""

import streamlit as st

from view.pages.detector import show_detector
from view.pages.logs import show_logs
from view.pages.admin.statistic_report import show_report as show_statistic_report
from view.pages.admin.user_management import show_user
from view.pages.admin.buildings_management import show_buildings
from view.pages.security_guard.security_detector import show_security_detector
from view.pages.security_guard.device_state import show_device_state
from view.pages.security_guard.issue_report import show_issue_report
from view.pages.supervision.field_report import show_report as show_field_report

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


def get_pages_for_role(role: int):
    """Trả về danh sách trang Dashboard tương ứng với role."""

    if role == 0:
        return {"Quản trị": [
            st.Page(
                show_statistic_report,
                title="Thống kê báo cáo",
                icon=":material/bar_chart:",
                url_path="statistics",
            ),
            st.Page(
                show_detector,
                title="Giám sát trực tiếp",
                icon=":material/videocam:",
                url_path="monitoring",
            ),
            st.Page(
                show_logs,
                title="Nhật ký vi phạm",
                icon=":material/menu_book:",
                url_path="logs",
            ),
            st.Page(
                show_buildings,
                title="Danh sách tòa nhà",
                icon=":material/apartment:",
                url_path="buildings",
            ),
            st.Page(
                show_user,
                title="Quản lý người dùng",
                icon=":material/group:",
                url_path="users",
            )]
        }

    if role == 1:
        return {
            "Giám sát": [
                st.Page(
                    show_detector,
                    title="Giám sát trực tiếp",
                    icon=":material/videocam:",
                    url_path="monitoring",
                ),
                st.Page(
                    show_logs,
                    title="Nhật ký vi phạm",
                    icon=":material/menu_book:",
                    url_path="logs",
                ),
                st.Page(
                    show_field_report,
                    title="Xuất biên bản",
                    icon=":material/description:",
                    url_path="field-report",
                ),
            ]
        }

    if role == 2:
        return {
            "An ninh": [
                st.Page(
                    show_security_detector,
                    title="Giám sát an ninh",
                    icon=":material/shield:",
                    url_path="security-monitoring",
                ),
                st.Page(
                    show_device_state,
                    title="Trạng thái thiết bị",
                    icon=":material/devices:",
                    url_path="device-state",
                ),
                st.Page(
                    show_issue_report,
                    title="Báo cáo sự cố",
                    icon=":material/report_problem:",
                    url_path="issue-report",
                ),
            ]
        }

    return {}
