import base64
import sqlite3
from pathlib import Path

import streamlit as st

from utils.database_path import getdatabase_path
from view.component.admin_table import render_admin_table

st.set_page_config(layout="wide", page_title="Quản lý người dùng")


def show_user():
    st.markdown(
        """
        <div class="page-header">
            <div>
                <h1 class="page-header-title">Quản lý người dùng</h1>
                <p class="page-header-subtitle">Theo dõi tài khoản EduWatch VNUA, vai trò và trạng thái hoạt động.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with sqlite3.connect(getdatabase_path()) as conn:
        db_users = conn.execute(
            """
            SELECT id, ma_giang_vien, ho_ten, so_dien_thoai, role, status
            FROM Users
            ORDER BY id
            """
        ).fetchall()

    default_avatar = Path(__file__).resolve().parents[3] / "data_model" / "avatar" / "default.jpg"
    avatar_data = ""
    if default_avatar.exists():
        encoded = base64.b64encode(default_avatar.read_bytes()).decode("ascii")
        avatar_data = f"data:image/jpeg;base64,{encoded}"

    users = [
        {
            "id": row[0],
            "name": row[2],
            "phone": row[3] or "",
            "username": row[1],
            "role": row[4],
            "status": row[5],
            "avatar": avatar_data,
        }
        for row in db_users
    ]

    render_admin_table("users", users, height=620)
