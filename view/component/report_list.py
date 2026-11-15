"""Bảng lịch sử báo cáo dùng chung (Báo cáo sự cố, Xuất biên bản, tab Thống kê).

Giao diện giống trang Nhật ký vi phạm: khối bộ lọc dạng form (nút làm mới + nút tìm),
bên dưới là bảng có thanh tìm kiếm / sắp xếp / xuất dữ liệu ngay trong bảng.
Dữ liệu đầu vào là DataFrame do src.services.load_report_record._load_records trả về.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
from datetime import date

from src.services.load_report_record import REPORT_SPECS
from utils.helper import _format_status, date_range_bounds
from view.component.admin_table import render_admin_table

STATUS_OPTIONS = ["Tất cả trạng thái", "Chờ xử lý", "Đã xác nhận", "Đã hủy"]

# kind -> (cột dùng cho bộ lọc phân loại, nhãn bộ lọc, nhãn "tất cả")
CATEGORY = {
    "issue": ("loai_su_co", "LOẠI SỰ CỐ", "Tất cả loại sự cố"),
    "field": ("mon_thi", "MÔN THI", "Tất cả môn thi"),
}
# kind -> cột chứa tên phòng trong dữ liệu báo cáo (tên tòa nhà luôn nằm ở cột "toa_nha").
ROOM_COLUMN = {"issue": "phong", "field": "phong_thi"}
ALL_PLACES = "Tất cả phòng học"
# 10 dòng + thanh công cụ + tiêu đề + chân bảng.
REPORT_TABLE_HEIGHT = 740


def _text(value) -> str:
    return "" if value is None or pd.isna(value) else str(value).strip()


def _place_label(row, room_column: str) -> str:
    """Nhãn "Tòa nhà / Phòng" của một báo cáo, cùng kiểu với bộ lọc ở Nhật ký vi phạm.

    Trả về chuỗi rỗng nếu báo cáo không ghi tòa nhà lẫn phòng.
    """
    building = _text(row.get("toa_nha"))
    room = _text(row.get(room_column))
    if not building and " - " in room:  # dữ liệu cũ ghi gộp "Tòa nhà - Phòng"
        building, _, room = room.rpartition(" - ")
    return " / ".join(part.strip() for part in (building, room) if part.strip())


def _default_filters() -> dict:
    # Mặc định hiển thị dữ liệu trong ngày hiện tại.
    today = date.today()
    return {"start": today, "end": today, "place": None, "title": None, "status": None}


def render_request_list(
    frame: pd.DataFrame,
    *,
    kind: str,
    key_prefix: str,
    height: int = REPORT_TABLE_HEIGHT,
    can_approve: bool = False,
) -> None:
    """kind: ``field`` cho biên bản, ``issue`` cho báo cáo sự cố."""
    if kind not in {"field", "issue"}:
        raise ValueError("kind phải là 'field' hoặc 'issue'.")

    applied_key = f"{key_prefix}_applied"
    widget_keys = [
        f"{key_prefix}_dates", f"{key_prefix}_place",
        f"{key_prefix}_title", f"{key_prefix}_status",
    ]

    # Đặt lại: xóa giá trị widget TRƯỚC khi tạo widget ở lượt chạy kế tiếp.
    if st.session_state.pop(f"{key_prefix}_reset", False):
        for key in widget_keys:
            st.session_state.pop(key, None)
        st.session_state[applied_key] = _default_filters()
    st.session_state.setdefault(applied_key, _default_filters())

    category_col, category_label, all_label = CATEGORY[kind]
    titles = sorted({t for t in frame[category_col].dropna().astype(str) if t}) if not frame.empty else []

    # Danh sách "Tòa nhà / Phòng" lấy từ chính các báo cáo (giống Nhật ký vi phạm lấy từ nhật ký).
    frame = frame.copy()
    room_column = ROOM_COLUMN[kind]
    frame["_place"] = (
        frame.apply(lambda row: _place_label(row, room_column), axis=1) if not frame.empty else []
    )
    places: dict[str, str] = {}
    for label in sorted(frame["_place"]):
        if label:
            places.setdefault(label.casefold(), label)

    with st.container(border=False, key=f"{key_prefix}_filter_box"):
        with st.form(f"{key_prefix}_filter_form", border=False):
            c1, c2, c3, c4, reset_col, search_col = st.columns([4.3, 4.3, 4.3, 4.3, 0.9, 0.9])
            with c1:
                date_range = st.date_input(
                    "KHOẢNG NGÀY",
                    value=(date.today(), date.today()),
                    format="DD/MM/YYYY",
                    key=widget_keys[0],
                )
            with c2:
                place_label = st.selectbox(
                    "TÒA NHÀ / PHÒNG HỌC", [ALL_PLACES, *places.values()], key=widget_keys[1]
                )
            with c3:
                title_label = st.selectbox(
                    category_label, [all_label, *titles], key=widget_keys[2]
                )
            with c4:
                status_label = st.selectbox(
                    "TRẠNG THÁI", STATUS_OPTIONS, key=widget_keys[3]
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
        start, end = date_range_bounds(date_range)
        st.session_state[applied_key] = {
            "start": start,
            "end": end,
            "place": None if place_label == ALL_PLACES else place_label,
            "title": None if title_label == all_label else title_label,
            "status": None if status_label == STATUS_OPTIONS[0] else status_label,
        }

    applied = st.session_state[applied_key]

    rows = frame.copy()
    if not rows.empty:
        if applied["start"] and applied["end"]:
            created = pd.to_datetime(rows["created_at"], errors="coerce")
            rows = rows[created.dt.date.between(applied["start"], applied["end"])]
        if applied.get("place"):
            rows = rows[rows["_place"].str.casefold() == applied["place"].casefold()]
        if applied["title"]:
            rows = rows[rows[category_col] == applied["title"]]
        if applied["status"]:
            rows = rows[rows["status"].map(_format_status) == applied["status"]]

    # Mỗi loại giữ đúng các cột riêng; khóa trong dữ liệu trùng tên cột database (xem admin_table.js).
    # Chỉ quản trị viên (role 0) ở trang Thống kê mới có quyền xác nhận / hủy.
    is_admin = bool(can_approve) and st.session_state.get("role") == 0
    admin_code = str(st.session_state.get("professor_id") or "") if is_admin else ""

    table_data = []
    for _, row in rows.iterrows():
        created_at = pd.to_datetime(row["created_at"], errors="coerce")
        item = {
            "id": row["id"],
            "created_at": str(row["created_at"]),  # dùng để sắp xếp đúng thứ tự thời gian
            "datetime_display": (
                created_at.strftime("%d/%m/%Y %H:%M") if pd.notna(created_at) else str(row["created_at"])
            ),
            "review_status": row["status"],
            "can_approve": is_admin,
            "admin_code": admin_code,
        }
        for field in REPORT_SPECS[kind][1]:
            item[field] = row[field]
        table_data.append(item)

    render_admin_table(
        "field_reports" if kind == "field" else "issue_reports",
        table_data,
        height=height,
        can_approve=can_approve,
    )
