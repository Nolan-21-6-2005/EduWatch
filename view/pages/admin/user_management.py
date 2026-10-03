import base64
import sqlite3
from pathlib import Path

import streamlit as st

from utils.database_path import getdatabase_path
from src.database_query.admin import get_users
from view.component.admin_table import render_admin_table

st.set_page_config(layout="wide", page_title="Quản lý người dùng")


<<<<<<< HEAD
def show_user():
    with sqlite3.connect(getdatabase_path()) as conn:
        db_users = conn.execute(
            """
            SELECT id, ma_giang_vien, ho_ten, so_dien_thoai, role, status
            FROM Users
            ORDER BY id
            """
        ).fetchall()

    default_avatar = (
        Path(__file__).resolve().parents[3]
        / "data_model"
        / "avatar"
        / "default.jpg"
    )

    avatar_data = ""

    if default_avatar.exists():
        encoded = base64.b64encode(
            default_avatar.read_bytes()
        ).decode("ascii")

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

    total_active = sum(
        int(row[5] or 0) == 1
        for row in db_users
    )

    active_teachers = sum(
        int(row[5] or 0) == 1
        and int(row[4] or -1) == 1
        for row in db_users
    )

    active_guards = sum(
        int(row[5] or 0) == 1
        and int(row[4] or -1) == 2
        for row in db_users
    )

    c1, c2, c3 = st.columns(3, gap="small")

    with c1:
        st.html(
            f'''
            <div class="ew-bottom-stat">
                <div class="ew-bottom-icon green">♣</div>
                <div>
                    <span>Tổng người dùng</span>
                    <strong>{total_active}</strong>
                    <small>Tài khoản đang hoạt động</small>
                </div>
            </div>
            ''',
        )

    with c2:
        st.html(
            f'''
            <div class="ew-bottom-stat">
                <div class="ew-bottom-icon blue">◆</div>
                <div>
                    <span>Giảng viên</span>
                    <strong>{active_teachers}</strong>
                    <small>Tài khoản giảng viên</small>
                </div>
            </div>
            ''',
        )

    with c3:
        st.html(
            f'''
            <div class="ew-bottom-stat">
                <div class="ew-bottom-icon orange">◇</div>
                <div>
                    <span>Bảo vệ</span>
                    <strong>{active_guards}</strong>
                    <small>Tài khoản bảo vệ</small>
                </div>
            </div>
            ''',
        )

    render_admin_table(
        "users",
        users,
        height=620,
    )
=======

with sqlite3.connect(getdatabase_path()) as conn:
    db_users = conn.execute(
        """
        SELECT id, ma_giang_vien, ho_ten, so_dien_thoai, role, status
        FROM Users
        ORDER BY id
        """
    ).fetchall()

default_avatar = (
    Path(__file__).resolve().parents[3]
    / "data_model"
    / "avatar"
    / "default.jpg"
)

avatar_data = ""

if default_avatar.exists():
    encoded = base64.b64encode(
        default_avatar.read_bytes()
    ).decode("ascii")

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

total_active = sum(
    int(row[5] or 0) == 1
    for row in db_users
)

active_teachers = sum(
    int(row[5] or 0) == 1
    and int(row[4] or -1) == 1
    for row in db_users
)

active_guards = sum(
    int(row[5] or 0) == 1
    and int(row[4] or -1) == 2
    for row in db_users
)

c1, c2, c3 = st.columns(3, gap="small")

with c1:
    st.html(
        f'''
        <div class="ew-bottom-stat">
            <div class="ew-bottom-icon green">♣</div>
            <div>
                <span>Tổng người dùng</span>
                <strong>{total_active}</strong>
                <small>Tài khoản đang hoạt động</small>
            </div>
        </div>
        ''',
    )

with c2:
    st.html(
        f'''
        <div class="ew-bottom-stat">
            <div class="ew-bottom-icon blue">◆</div>
            <div>
                <span>Giảng viên</span>
                <strong>{active_teachers}</strong>
                <small>Tài khoản giảng viên</small>
            </div>
        </div>
        ''',
    )

with c3:
    st.html(
        f'''
        <div class="ew-bottom-stat">
            <div class="ew-bottom-icon orange">◇</div>
            <div>
                <span>Bảo vệ</span>
                <strong>{active_guards}</strong>
                <small>Tài khoản bảo vệ</small>
            </div>
        </div>
        ''',
    )

render_admin_table(
    "users",
    users,
    height=620,
)
>>>>>>> 81d7401 (update)
