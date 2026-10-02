from __future__ import annotations

import hashlib
import sqlite3
from utils.database_path import getdatabase_path


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(getdatabase_path())
    conn.row_factory = sqlite3.Row
    return conn


def get_users() -> list[dict]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT id, ma_giang_vien, ho_ten, so_dien_thoai, role, status,
                   anh_dai_dien, email, ngay_sinh, gioi_tinh, created_at
            FROM Users
            ORDER BY id ASC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def update_user_role(user_id: int, role: int) -> None:
    if int(role) not in {0, 1, 2}:
        raise ValueError("Vai trò không hợp lệ.")
    with _connect() as conn:
        cur = conn.execute("UPDATE Users SET role=? WHERE id=?", (int(role), int(user_id)))
        if cur.rowcount == 0:
            raise ValueError("Không tìm thấy tài khoản.")
        conn.commit()


def update_user_status(user_id: int, status: int) -> None:
    with _connect() as conn:
        cur = conn.execute("UPDATE Users SET status=? WHERE id=?", (1 if int(status) else 0, int(user_id)))
        if cur.rowcount == 0:
            raise ValueError("Không tìm thấy tài khoản.")
        conn.commit()


def reset_user_password(user_id: int, password: str) -> None:
    value = password.strip()
    if len(value) < 6:
        raise ValueError("Mật khẩu mới cần ít nhất 6 ký tự.")
    password_hash = hashlib.sha256(value.encode()).hexdigest()
    with _connect() as conn:
        cur = conn.execute("UPDATE Users SET password=? WHERE id=?", (password_hash, int(user_id)))
        if cur.rowcount == 0:
            raise ValueError("Không tìm thấy tài khoản.")
        conn.commit()


def delete_user(user_id: int) -> None:
    # Giữ lịch sử tham chiếu; tài khoản được đưa về trạng thái khóa.
    update_user_status(user_id, 0)


def get_user_by_code(code: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT id, ma_giang_vien, ho_ten, role, status, anh_dai_dien
            FROM Users
            WHERE ma_giang_vien=?
            LIMIT 1
            """,
            (code,),
        ).fetchone()
    return dict(row) if row else None
