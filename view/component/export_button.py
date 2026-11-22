"""Nút "Xuất dữ liệu" (CSV) đặt cùng dòng với tiêu đề trang.

Nút là st.download_button của Streamlit nên nằm ngoài bảng. Dữ liệu xuất là đúng các dòng đang
được lọc (cùng dữ liệu đưa vào bảng); cột trạng thái ghi bằng nhãn tiếng Việt.

Cách dùng: tạo chỗ đặt nút ngay trong hàng tiêu đề, rồi điền sau khi đã có dữ liệu.

    title_col, export_col = st.columns([6, 1.4], vertical_alignment="center")
    title_col.header("Nhật ký vi phạm")
    export_slot = export_col.empty()
    ...
    render_export_button(export_slot, "violations", data)
"""
from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Callable

import streamlit as st

VIOLATION_STATUS = {"pending": "Chờ xác nhận", "confirmed": "Đã xác nhận", "wrong": "Báo sai AI"}
REQUEST_STATUS = {
    "pending": "Chờ xử lý", "processing": "Đang xử lý", "resolved": "Đã xác nhận", "rejected": "Đã hủy",
}


def _status(labels: dict[str, str], default: str) -> Callable:
    return lambda value: labels.get(str(value or "").lower(), default)


def _percent(value) -> str:
    try:
        return f"{float(value) * 100:.1f}"
    except (TypeError, ValueError):
        return ""


# loại bảng -> (tên tệp, [(khóa dữ liệu, tiêu đề cột CSV, hàm định dạng hoặc None)])
EXPORTS: dict[str, tuple[str, list[tuple[str, str, Callable | None]]]] = {
    "violations": ("nhat_ky_vi_pham", [
        ("id", "ID", None),
        ("title", "Loại vi phạm", None),
        ("datetime_display", "Thời gian", None),
        ("building", "Tòa nhà", None),
        ("room", "Phòng", None),
        ("camera", "Góc camera", None),
        ("confidence", "Độ tin cậy (%)", _percent),
        ("review_status", "Trạng thái", _status(VIOLATION_STATUS, "Chờ xác nhận")),
    ]),
    "issue_reports": ("bao_cao_su_co", [
        ("datetime_display", "Thời gian", None),
        ("loai_su_co", "Loại sự cố", None),
        ("toa_nha", "Tòa nhà", None),
        ("phong", "Phòng", None),
        ("mo_ta", "Mô tả", None),
        ("review_status", "Trạng thái", _status(REQUEST_STATUS, "Chờ xử lý")),
    ]),
    "field_reports": ("bien_ban", [
        ("datetime_display", "Thời gian", None),
        ("mon_thi", "Môn thi", None),
        ("toa_nha", "Tòa nhà", None),
        ("phong_thi", "Phòng thi", None),
        ("ghi_chu", "Ghi chú", None),
        ("review_status", "Trạng thái", _status(REQUEST_STATUS, "Chờ xử lý")),
    ]),
}


def build_csv(kind: str, rows: list[dict]) -> bytes:
    """CSV (UTF-8 có BOM để Excel đọc đúng tiếng Việt) của các dòng đang hiển thị."""
    _, columns = EXPORTS[kind]
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, quoting=csv.QUOTE_ALL)
    writer.writerow([label for _, label, _ in columns])
    for row in rows:
        writer.writerow([
            (fmt(row.get(key)) if fmt else ("" if row.get(key) is None else row.get(key)))
            for key, _, fmt in columns
        ])
    return buffer.getvalue().encode("utf-8-sig")


def render_export_button(slot, kind: str, rows: list[dict], *, label: str = "Xuất dữ liệu") -> None:
    """Đặt nút tải CSV vào `slot` (st.empty() hoặc một cột). Không có dữ liệu thì nút bị khóa."""
    file_prefix, _ = EXPORTS[kind]
    slot.download_button(
        f":material/download:  {label}",
        data=build_csv(kind, rows),
        file_name=f"{file_prefix}_{datetime.now():%Y%m%d_%H%M}.csv",
        mime="text/csv",
        key=f"export_{kind}",
        on_click="ignore",  # tải xuống không làm trang chạy lại (giữ nguyên bảng đang xem)
        disabled=not rows,
        use_container_width=True,
    )
