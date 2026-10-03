from __future__ import annotations

import hashlib
from typing import Any
import sqlite3
from utils.database_path import getdatabase_path


def get_user_by_id(user_id: int):
    with sqlite3.connect(getdatabase_path()) as conn:
        conn.row_factory = sqlite3.Row
        
        row = conn.execute(
            """
            SELECT
                id,
                ma_giang_vien,
                ho_ten,
                ngay_sinh,
                gioi_tinh,
                email,
                so_dien_thoai,
                role,
                status,
                anh_dai_dien,
                created_at
            FROM Users
            WHERE id = ?
            LIMIT 1
            """,
            (int(user_id),),
        ).fetchone()
    if row is None: return None

    return {
        key: row[key]
        for key in row.keys()
    }


def get_user_by_code(code: str):
    with sqlite3.connect(getdatabase_path()) as conn:
        conn.row_factory = sqlite3.Row
        
        row = conn.execute(
            """
            SELECT
                id,
                ma_giang_vien,
                ho_ten,
                ngay_sinh,
                gioi_tinh,
                email,
                so_dien_thoai,
                role,
                status,
                anh_dai_dien,
                created_at
            FROM Users
            WHERE ma_giang_vien = ?
            LIMIT 1
            """,
            (code.strip(),),
        ).fetchone()
    if row is None: return None

    return {
        key: row[key]
        for key in row.keys()
    }


def phone_exists(phone: str, exclude_user_id: int | None = None) -> bool:
    value = phone.strip()
    if not value:
        return False

    query = "SELECT 1 FROM Users WHERE so_dien_thoai = ?"
    params: list[object] = [value]

    if exclude_user_id is not None:
        query += " AND id != ?"
        params.append(int(exclude_user_id))

    query += " LIMIT 1"

    with sqlite3.connect(getdatabase_path()) as conn:
        return conn.execute(query, params).fetchone() is not None


def update_profile_contact(
    user_id: int,
    so_dien_thoai: str,
    anh_dai_dien: str | None = None,
) -> dict[str, Any] | None:
    with sqlite3.connect(getdatabase_path()) as conn:
        if anh_dai_dien:
            conn.execute(
                """
                UPDATE Users
                SET so_dien_thoai = ?, anh_dai_dien = ?
                WHERE id = ?
                """,
                (so_dien_thoai.strip(), anh_dai_dien, int(user_id)),
            )
        else:
            conn.execute(
                """
                UPDATE Users
                SET so_dien_thoai = ?
                WHERE id = ?
                """,
                (so_dien_thoai.strip(), int(user_id)),
            )
        conn.commit()

    return get_user_by_id(int(user_id))


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(user_id: int, password: str) -> bool:
    password_hash = hash_password(password)

    with sqlite3.connect(getdatabase_path()) as conn:
        row = conn.execute(
            "SELECT 1 FROM Users WHERE id = ? AND password = ? LIMIT 1",
            (int(user_id), password_hash),
        ).fetchone()

    return row is not None


def update_password(user_id: int, new_password: str) -> None:
    with sqlite3.connect(getdatabase_path()) as conn:
        conn.execute(
            "UPDATE Users SET password = ? WHERE id = ?",
            (hash_password(new_password), int(user_id)),
        )
        conn.commit()
