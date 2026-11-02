"""Shared list/filter renderer for teacher field reports and guard incident reports."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.config import start_date, end_date
from utils.helper import _format_status
from view.component.admin_table import render_admin_table


def render_request_list(
    frame: pd.DataFrame,
    *,
    kind: str,
    key_prefix: str,
    height: int = 520,
) -> None:
    """Render a request list with shared date/status/category filters.

    kind: ``field`` for exam reports, ``issue`` for incident reports.
    """
    if kind not in {"field", "issue"}:
        raise ValueError("kind phải là 'field' hoặc 'issue'.")

    category_label = "Loại sự cố"
    category_candidates = (
        {"loai_su_co", "issue_type", "tieu_de", "mon_thi", "subject", "course", "ten_mon"}
        if kind == "field"
        else {"loai_su_co", "issue_type", "subject", "loai"}
    )
    category_col = next(
        (c for c in frame.columns if str(c).strip().lower() in category_candidates),
        None,
    )

    date_col, status_col, category_filter_col, search_col = st.columns(
        [1.6, 1.0, 1.2, 1.5], vertical_alignment="bottom"
    )
    with date_col:
        date_range = st.date_input(
            "KHOẢNG NGÀY",
            value=(start_date, end_date),
            format="DD/MM/YYYY",
            key=f"{key_prefix}_date_range",
        )
    with status_col:
        status_filter = st.selectbox(
            "Trạng thái",
            ["Tất cả", "Chờ xử lý", "Đã xử lý"],
            key=f"{key_prefix}_status",
            width="stretch",
        )
    options = ["Tất cả"]
    if category_col and not frame.empty:
        options += sorted(frame[category_col].dropna().astype(str).unique().tolist())
    with category_filter_col:
        category_filter = st.selectbox(
            category_label,
            options,
            key=f"{key_prefix}_category",
            width="stretch",
        )
    with search_col:
        query = st.text_input(
            "TÌM KIẾM",
            placeholder="Nội dung, phòng, người gửi...",
            key=f"{key_prefix}_search",
        )

    filtered = frame.copy()
    if not filtered.empty:
        if "status" in filtered.columns:
            filtered["_status_label"] = filtered["status"].map(_format_status)
            if status_filter != "Tất cả":
                filtered = filtered[filtered["_status_label"] == status_filter]

        if category_filter != "Tất cả" and category_col:
            filtered = filtered[filtered[category_col].astype(str) == category_filter]

        selected_start = selected_end = None
        if isinstance(date_range, (tuple, list)):
            if len(date_range) == 2:
                selected_start, selected_end = date_range
            elif len(date_range) == 1:
                selected_start = selected_end = date_range[0]
        elif date_range:
            selected_start = selected_end = date_range

        if selected_start is not None and selected_end is not None:
            created_col = next(
                (c for c in ("created_at", "request_created_at", "created_date", "ngay_tao")
                 if c in filtered.columns),
                None,
            )
            if created_col:
                parsed = pd.to_datetime(filtered[created_col], errors="coerce")
                filtered = filtered[parsed.dt.date.between(selected_start, selected_end)]

        if query.strip():
            searchable = filtered.astype(str).apply(
                lambda column: column.str.contains(query.strip(), case=False, na=False)
            ).any(axis=1)
            filtered = filtered[searchable]

        table_data = []
        for _, row in filtered.iterrows():
            report = row.get("request_data", {})
            if not isinstance(report, dict):
                report = {}

            if kind == "field":
                room_value = (
                    report.get("phong_hoc")
                    or report.get("phong_thi")
                    or report.get("phong")
                    or "--"
                )
                building_value = (
                    report.get("toa_nha")
                    or report.get("ten_toa")
                    or report.get("building")
                    or "--"
                )
                # Biên bản cũ có thể lưu vị trí theo dạng
                # "Tên tòa nhà - Mã phòng" trong trường phong_thi.
                if building_value == "--" and isinstance(room_value, str) and " - " in room_value:
                    building_value, room_value = room_value.rsplit(" - ", 1)

                table_data.append({
                    "id": row.get("id", ""),
                    "datetime_display": str(row.get("created_at", "--")),
                    "building": building_value,
                    "room": room_value,
                    "title": (
                        report.get("loai_su_co")
                        or report.get("tieu_de")
                        or report.get("mon_thi")
                        or row.get("subject")
                        or "Chưa xác định"
                    ),
                    "description": (
                        report.get("mo_ta")
                        or report.get("noi_dung")
                        or report.get("ghi_chu")
                        or ""
                    ),
                    "review_status": row.get("status", "pending"),
                })
            else:
                table_data.append({
                    "id": row.get("id", ""),
                    "datetime_display": str(row.get("created_at", "--")),
                    "building": (
                        report.get("toa_nha")
                        or report.get("ten_toa")
                        or report.get("building")
                        or "--"
                    ),
                    "room": (
                        report.get("phong_hoc")
                        or report.get("phong")
                        or report.get("room")
                        or "--"
                    ),
                    "title": (
                        report.get("loai_su_co")
                        or report.get("issue_type")
                        or row.get("subject")
                        or "Sự cố chưa xác định"
                    ),
                    "description": (
                        report.get("mo_ta")
                        or report.get("description")
                        or report.get("noi_dung")
                        or ""
                    ),
                    "review_status": row.get("status", "pending"),
                })

        render_admin_table(
            "field_reports" if kind == "field" else "issue_reports",
            table_data,
            height=height,
        )
        st.caption(f"{len(filtered)} {('biên bản' if kind == 'field' else 'báo cáo')} phù hợp")
        csv = filtered.drop(columns=["_status_label"], errors="ignore").to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Xuất danh sách CSV",
            data=csv,
            file_name="bien_ban_ca_thi.csv" if kind == "field" else "bao_cao_su_co.csv",
            mime="text/csv",
            key=f"{key_prefix}_export",
        )
    else:
        render_admin_table(
            "field_reports" if kind == "field" else "issue_reports",
            [],
            height=height,
        )
        st.info("Chưa có dữ liệu lịch sử để hiển thị.")
