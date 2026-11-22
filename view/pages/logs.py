import streamlit as st
from datetime import date, datetime
from pathlib import Path

from src.database_query.violation_logs import get_violation_logs
from src.services.violation_log_services import _image_url
from utils.helper import date_range_bounds
from view.component.admin_table import render_admin_table
from view.component.export_button import render_export_button


st.set_page_config(layout="wide", page_title="Nhật ký vi phạm")

# Lấy toàn bộ nhật ký ban đầu.
all_rows = get_violation_logs()

# Tạo danh sách phòng học, tránh trùng lựa chọn khi một phòng có nhiều log.
room_options = {"Tất cả phòng học": None}
for row in all_rows:
    room_id = row["room_id"]
    if room_id is None:
        continue

    building_name = row["ten_toa"] or "Không xác định"
    room_name = row["ten_phong"] or "Không xác định"
    room_options.setdefault(f"{building_name} / {room_name}", room_id)

types = sorted({
    row["loai_vi_pham"]
    for row in all_rows
    if row["loai_vi_pham"]
})


FILTER_WIDGET_KEYS = [
    "log_date_range", "log_building", "log_session", "log_type", "log_status",
]


def empty_filters():
    # Mặc định chỉ hiển thị dữ liệu của ngày hiện tại.
    today = date.today().isoformat()
    return {
        "room_id": None,
        "violation_type": None,
        "review_status": None,
        "start_date": today,
        "end_date": today,
        "session": None,
    }


# Đặt lại: xóa giá trị các ô nhập TRƯỚC khi tạo widget ở lượt chạy này.
if st.session_state.pop("reset_log_filters", False):
    for widget_key in FILTER_WIDGET_KEYS:
        st.session_state.pop(widget_key, None)


if "violation_applied_filters" not in st.session_state:
    st.session_state["violation_applied_filters"] = empty_filters()


# Tiêu đề trang; nút "Xuất dữ liệu" nằm cùng dòng, bên phải (điền sau khi có dữ liệu).
title_col, export_col = st.columns([6, 1.4], vertical_alignment="center")
title_col.header("Nhật ký vi phạm")
export_slot = export_col.empty()

# Bộ lọc.
with st.container(border=False, key="violation_filter_box"):
    with st.form("violation_filter_form", border=False):
        c1, c2, c3, c4, c5, reset_col, search_col = st.columns(
            [4.3, 4.3, 4.3, 4.3, 4.3, 0.9, 0.9]
        )

        with c1:
            date_range = st.date_input(
                "KHOẢNG NGÀY",
                value=(date.today(), date.today()),
                format="DD/MM/YYYY",
                key="log_date_range",
            )

        with c2:
            selected_room = st.selectbox(
                "TÒA NHÀ / PHÒNG HỌC",
                options=list(room_options.keys()),
                key="log_building",
            )

        with c3:
            session_label = st.selectbox(
                "CHẾ ĐỘ",
                options=["Tất cả", "Phòng thi", "Phòng thường"],
                key="log_session",
            )

        with c4:
            type_label = st.selectbox(
                "LOẠI VI PHẠM",
                options=["Tất cả vi phạm", *types],
                key="log_type",
            )

        with c5:
            status_label = st.selectbox(
                "TRẠNG THÁI",
                options=[
                    "Tất cả trạng thái",
                    "Chờ xác nhận",
                    "Đã xác nhận",
                    "Báo sai AI",
                ],
                key="log_status",
            )

        with search_col:
            with st.container(vertical_alignment="bottom", height="stretch"):
                submitted = st.form_submit_button(
                    ":material/search:",
                    type="primary",
                    use_container_width=True,
                )

        with reset_col:
            with st.container(vertical_alignment="bottom", height="stretch"):
                reset = st.form_submit_button(
                    ":material/refresh:",
                    use_container_width=True,
                )


# Chỉ cập nhật điều kiện lọc khi nhấn Tìm kiếm hoặc Đặt lại.
if reset:
    st.session_state["violation_applied_filters"] = empty_filters()
    st.session_state["reset_log_filters"] = True
    st.rerun()
elif submitted:
    selected_room_id = room_options[selected_room]

    start_date_value, end_date_value = date_range_bounds(date_range)

    status_key = {
        "Chờ xác nhận": "pending",
        "Đã xác nhận": "confirmed",
        "Báo sai AI": "wrong",
    }.get(status_label)

    st.session_state["violation_applied_filters"] = {
        "room_id": selected_room_id,
        "violation_type": (
            None if type_label == "Tất cả vi phạm" else type_label
        ),
        "review_status": (
            None if status_label == "Tất cả trạng thái" else status_key
        ),
        "start_date": (
            start_date_value.isoformat() if start_date_value else None
        ),
        "end_date": (
            end_date_value.isoformat() if end_date_value else None
        ),
        "session": {
            "Phòng thi": "exam",
            "Phòng thường": "study",
        }.get(session_label),
    }


# Truy vấn SQL với các điều kiện được hỗ trợ.
applied_filters = st.session_state["violation_applied_filters"]
query_filters = {
    key: value
    for key, value in applied_filters.items()
    if key in {
        "room_id",
        "violation_type",
        "review_status",
        "start_date",
        "end_date",
    }
    and value is not None
}

filtered_rows = (
    get_violation_logs(**query_filters)
    if query_filters
    else all_rows
)

# Lọc chế độ tại tầng giao diện.
session_filter = applied_filters.get("session")
if session_filter is not None:
    filtered_rows = [
        row for row in filtered_rows
        if row["session"] == session_filter
    ]


# Chuẩn bị dữ liệu cho bảng.
data = []
for row in filtered_rows:
    raw_time = str(row["thoi_gian"] or "")
    try:
        display_time = datetime.fromisoformat(
            raw_time.replace("T", " ")
        ).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        display_time = raw_time

    image_path = row["image_path"] or ""
    data.append({
        "id": row["id"],
        "title": row["loai_vi_pham"] or "Vi phạm chưa xác định",
        "camera": row["vi_tri_goc"] or "Camera không xác định",
        "datetime_display": display_time,
        "thoi_gian": raw_time,
        "building": row["ten_toa"] or "--",
        "room": row["ten_phong"] or "--",
        "confidence": float(row["confidence"] or 0),
        "review_status": row["review_status"] or "pending",
        "image": _image_url(image_path),  # URL, không nhúng base64 (tránh vượt giới hạn data URL)
        "image_is_illustrative": Path(str(image_path)).name.startswith("illustrative_"),
    })

render_export_button(export_slot, "violations", data)
render_admin_table("violations", data, height=690, toolbar="none")
