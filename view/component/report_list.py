"""Bảng lịch sử báo cáo dùng chung (Báo cáo sự cố, Xuất biên bản, tab Thống kê).

Giao diện giống trang Nhật ký vi phạm: khối bộ lọc dạng form (nút làm mới + nút tìm),
bên dưới là bảng có thanh tìm kiếm / sắp xếp / xuất dữ liệu ngay trong bảng.
Dữ liệu đầu vào là DataFrame do src.services.load_report_record._load_records trả về.
"""
from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from src.services.load_report_record import REPORT_SPECS
from utils.helper import _format_status
from view.component.admin_table import render_admin_table

STATUS_OPTIONS = ["Tất cả trạng thái", "Chờ xử lý", "Đã xử lý"]

# kind -> (cột dùng cho bộ lọc phân loại, nhãn bộ lọc, nhãn "tất cả")
CATEGORY = {
    "issue": ("loai_su_co", "LOẠI SỰ CỐ", "Tất cả loại sự cố"),
    "field": ("mon_thi", "MÔN THI", "Tất cả môn thi"),
}
# 10 dòng + thanh công cụ + tiêu đề + chân bảng.
REPORT_TABLE_HEIGHT = 740


def _default_dates() -> tuple[date, date]:
    """7 ngày gần nhất tính đến hôm nay (tính lại mỗi lần chạy, không cố định lúc import)."""
    today = date.today()
    return today - timedelta(days=6), today


def _default_filters() -> dict:
    start, end = _default_dates()
    return {"start": start, "end": end, "title": None, "status": None}


def _as_range(value) -> tuple[date, date] | None:
    # Khi mới chọn ngày đầu, date_input trả về 1 phần tử: coi như lọc đúng ngày đó.
    if isinstance(value, (tuple, list)):
        if len(value) == 2:
            return value[0], value[1]
        if len(value) == 1:
            return value[0], value[0]
        return None
    return (value, value) if value else None


def render_request_list(
    frame: pd.DataFrame,
    *,
    kind: str,
    key_prefix: str,
    height: int = REPORT_TABLE_HEIGHT,
) -> None:
    """kind: ``field`` cho biên bản, ``issue`` cho báo cáo sự cố."""
    if kind not in {"field", "issue"}:
        raise ValueError("kind phải là 'field' hoặc 'issue'.")

    applied_key = f"{key_prefix}_applied"
    widget_keys = [f"{key_prefix}_dates", f"{key_prefix}_title", f"{key_prefix}_status"]

    # Đặt lại: xóa giá trị widget TRƯỚC khi tạo widget ở lượt chạy kế tiếp.
    if st.session_state.pop(f"{key_prefix}_reset", False):
        for key in widget_keys:
            st.session_state.pop(key, None)
        st.session_state[applied_key] = _default_filters()
    st.session_state.setdefault(applied_key, _default_filters())

    category_col, category_label, all_label = CATEGORY[kind]
    titles = sorted({t for t in frame[category_col].dropna().astype(str) if t}) if not frame.empty else []
    start_default, end_default = _default_dates()

    with st.container(border=False, key=f"{key_prefix}_filter_box"):
        with st.form(f"{key_prefix}_filter_form", border=False):
            c1, c2, c3, reset_col, search_col = st.columns([4.3, 4.3, 4.3, 0.9, 0.9])
            with c1:
                date_range = st.date_input(
                    "KHOẢNG NGÀY",
                    value=(start_default, end_default),
                    format="DD/MM/YYYY",
                    key=widget_keys[0],
                )
            with c2:
                title_label = st.selectbox(
                    category_label, [all_label, *titles], key=widget_keys[1]
                )
            with c3:
                status_label = st.selectbox(
                    "TRẠNG THÁI", STATUS_OPTIONS, key=widget_keys[2]
                )
            with search_col:
                with st.container(vertical_alignment="bottom", height="stretch"):
                    submitted = st.form_submit_button(
                        ":material/search:", type="primary", use_container_width=True
                    )
            with reset_col:
                with st.container(vertical_alignment="bottom", height="stretch"):
                    reset = st.form_submit_button(":material/refresh:", use_container_width=True)

    if reset:
        st.session_state[f"{key_prefix}_reset"] = True
        st.rerun()
    elif submitted:
        span = _as_range(date_range) or (start_default, end_default)
        st.session_state[applied_key] = {
            "start": span[0],
            "end": span[1],
            "title": None if title_label == all_label else title_label,
            "status": None if status_label == STATUS_OPTIONS[0] else status_label,
        }

    applied = st.session_state[applied_key]

    rows = frame.copy()
    if not rows.empty:
        created = pd.to_datetime(rows["created_at"], errors="coerce")
        rows = rows[created.dt.date.between(applied["start"], applied["end"])]
        if applied["title"]:
            rows = rows[rows[category_col] == applied["title"]]
        if applied["status"]:
            rows = rows[rows["status"].map(_format_status) == applied["status"]]

    # Mỗi loại giữ đúng các cột riêng; khóa trong dữ liệu trùng tên cột database (xem admin_table.js).
    table_data = []
    for _, row in rows.iterrows():
        created_at = pd.to_datetime(row["created_at"], errors="coerce")
        item = {
            "id": row["id"],
            "created_at": str(row["created_at"]),  # dùng để sắp xếp đúng thứ tự thời gian
            "datetime_display": (
                created_at.strftime("%d/%m/%Y %H:%M:%S") if pd.notna(created_at) else str(row["created_at"])
            ),
            "review_status": row["status"],
        }
        for field in REPORT_SPECS[kind][1]:
            item[field] = row[field]
        table_data.append(item)

    render_admin_table(
        "field_reports" if kind == "field" else "issue_reports",
        table_data,
        height=height,
    )
