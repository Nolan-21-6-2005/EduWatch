"""Nạp lịch sử báo cáo từ bảng System_Requests, tách theo loai_yeu_cau.

  loai_yeu_cau = "su_co"    -> báo cáo sự cố (bảo vệ):   loai_su_co, toa_nha, phong, mo_ta
  loai_yeu_cau = "bien_ban" -> biên bản (giảng viên):     mon_thi, phong_thi, ghi_chu
Mỗi loại giữ nguyên các cột riêng của nó; không gộp hai loại vào một bộ cột.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.database_query import notifications as db

# kind -> (loai_yeu_cau trong database, các khóa lấy từ cột noi_dung (JSON))
REPORT_SPECS = {
    "issue": (db.REQUEST_INCIDENT, ("loai_su_co", "toa_nha", "phong", "mo_ta")),
    "field": (db.REQUEST_FIELD_REPORT, ("mon_thi", "phong_thi", "ghi_chu")),
}


def report_columns(kind: str) -> list[str]:
    return ["id", "created_at", *REPORT_SPECS[kind][1], "status"]


def _load_records(kind: str, *, all_users: bool = False) -> pd.DataFrame:
    """kind: "issue" (su_co) hoặc "field" (bien_ban).

    Mặc định chỉ lấy của tài khoản đang đăng nhập; all_users=True lấy của mọi người
    (trang Thống kê của quản trị viên).
    """
    if kind not in REPORT_SPECS:
        raise ValueError("kind phải là 'issue' hoặc 'field'.")
    request_type, fields = REPORT_SPECS[kind]
    columns = report_columns(kind)

    user_code = None
    if not all_users:
        user_code = st.session_state.get("professor_id")
        if not user_code:
            return pd.DataFrame(columns=columns)

    # System_Requests đã lọc theo loai_yeu_cau; noi_dung (JSON) được giải mã thành request_data.
    records = db._list_requests(user_code=user_code, request_type=request_type)

    rows = []
    for record in records:
        data = record.get("request_data")
        data = data if isinstance(data, dict) else {}
        rows.append({
            "id": record.get("id", ""),
            "created_at": record.get("created_at", ""),
            **{field: str(data.get(field) or "").strip() for field in fields},
            "status": record.get("status", "pending"),  # trang_thai: 0 -> pending, 1 -> resolved
        })
    return pd.DataFrame(rows, columns=columns)
