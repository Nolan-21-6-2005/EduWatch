import streamlit as st

from src.database_query.admin import get_users
from src.services.avatar_services import file_to_data_uri, resolve_avatar_path
from view.component.admin_table import render_admin_table
from view.component.metric import kpi_metric

st.set_page_config(layout="wide", page_title="Quản lý người dùng")

db_users = get_users()
users = [
    {
        "id": row["id"],
        "name": row["ho_ten"],
        "phone": row["so_dien_thoai"] or "",
        "username": row["ma_giang_vien"],
        "role": int(row["role"] if row["role"] is not None else -1),
        "status": int(row["status"] or 0),
        "avatar": file_to_data_uri(resolve_avatar_path(row.get("anh_dai_dien"))),
    }
    for row in db_users
]

total_active = sum(user["status"] == 1 for user in users)
active_teachers = sum(
    user["status"] == 1 and user["role"] == 1 for user in users
)
active_guards = sum(
    user["status"] == 1 and user["role"] == 2 for user in users
)

c1, c2, c3 = st.columns(3, gap="small")
with c1:
    kpi_metric(total_active, "Số lượng nhân sự", "Số lượng nhân sự của học viện", "green")
with c2:
    kpi_metric(active_teachers, "Số lượng giảng viên", "Số lượng giảng viên của học viện", "blue")
with c3:
    kpi_metric(active_guards, "Số lượng bảo vệ", "Số lượng bảo vệ của học viện", "orange")

render_admin_table("users", users, height=620)
