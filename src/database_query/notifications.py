from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime

from utils.helper import getdatabase_path

REQUEST_FIELD_REPORT = "bien_ban"   # giảng viên lập biên bản
REQUEST_INCIDENT = "su_co"          # bảo vệ báo cáo sự cố
STATUS_PENDING = 0
STATUS_APPROVED = 1
NOTI_NEW_REQUEST = "new_request"            # gửi tới admin
NOTI_REQUEST_APPROVED = "request_approved"  # gửi tới người gửi

ROLE_LABELS = {0: "Quản trị viên", 1: "Giảng viên", 2: "Bảo vệ"}
_TITLES = {
    REQUEST_FIELD_REPORT: {
        NOTI_NEW_REQUEST: "Biên bản mới từ giảng viên",
        NOTI_REQUEST_APPROVED: "Biên bản của bạn đã được duyệt",
    },
    REQUEST_INCIDENT: {
        NOTI_NEW_REQUEST: "Báo cáo sự cố mới từ bảo vệ",
        NOTI_REQUEST_APPROVED: "Báo cáo sự cố của bạn đã được duyệt",
    },
}

_DDL = """
CREATE TABLE IF NOT EXISTS Notifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,   -- người NHẬN
    request_id  INTEGER,
    loai        TEXT NOT NULL,
    tieu_de     TEXT NOT NULL,
    noi_dung    TEXT,
    is_read     INTEGER DEFAULT 0,
    created_at  TIMESTAMP,
    FOREIGN KEY(user_id)    REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY(request_id) REFERENCES System_Requests(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON Notifications(user_id, is_read);
"""
_schema_ready = False


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(_DDL)


@contextmanager
def _db():
    global _schema_ready
    conn = sqlite3.connect(getdatabase_path(), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if not _schema_ready:
        ensure_schema(conn)
        _schema_ready = True
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _now() -> str:
    # Giờ local (CURRENT_TIMESTAMP của SQLite là UTC nên không dùng)
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _summary(loai: str, data: dict) -> str:
    if loai == REQUEST_FIELD_REPORT:
        parts = [data.get("mon_thi"), data.get("phong_thi")]
    else:
        parts = [data.get("loai_su_co"), data.get("toa_nha"), data.get("phong")]
    return " · ".join(str(p) for p in parts if p)


def get_user_id(user_code: str) -> int | None:
    if not user_code:
        return None
    with _db() as conn:
        row = conn.execute("SELECT id FROM Users WHERE ma_giang_vien = ?", (user_code,)).fetchone()
    return row["id"] if row else None


def create_request(user_code: str, loai: str, data: dict) -> int:
    """Lưu yêu cầu và gửi thông báo tới mọi admin đang hoạt động."""
    if loai not in _TITLES:
        raise ValueError(f"Loại yêu cầu không hợp lệ: {loai}")
    with _db() as conn:
        sender = conn.execute(
            "SELECT id, ho_ten FROM Users WHERE ma_giang_vien = ? AND status = 1", (user_code,)
        ).fetchone()
        if sender is None:
            raise ValueError("Không tìm thấy tài khoản đang hoạt động.")
        now = _now()
        request_id = conn.execute(
            "INSERT INTO System_Requests (user_id, loai_yeu_cau, noi_dung, trang_thai, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (sender["id"], loai, json.dumps(data, ensure_ascii=False), STATUS_PENDING, now),
        ).lastrowid
        admins = conn.execute("SELECT id FROM Users WHERE role = 0 AND status = 1").fetchall()
        preview = f"{sender['ho_ten']}: {_summary(loai, data)}"
        conn.executemany(
            "INSERT INTO Notifications (user_id, request_id, loai, tieu_de, noi_dung, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            [(a["id"], request_id, NOTI_NEW_REQUEST, _TITLES[loai][NOTI_NEW_REQUEST], preview, now)
             for a in admins],
        )
    return request_id


def approve_request(request_id: int, admin_code: str) -> bool:
    """Admin duyệt và báo ngược cho người gửi. False nếu đã được duyệt trước đó."""
    with _db() as conn:
        admin = conn.execute(
            "SELECT id, ho_ten FROM Users WHERE ma_giang_vien = ? AND role = 0 AND status = 1",
            (admin_code,),
        ).fetchone()
        if admin is None:
            raise PermissionError("Chỉ quản trị viên mới được duyệt yêu cầu.")
        req = conn.execute(
            "SELECT user_id, loai_yeu_cau, noi_dung FROM System_Requests WHERE id = ?", (request_id,)
        ).fetchone()
        if req is None or req["loai_yeu_cau"] not in _TITLES:
            return False
        changed = conn.execute(
            "UPDATE System_Requests SET trang_thai = ? WHERE id = ? AND trang_thai = ?",
            (STATUS_APPROVED, request_id, STATUS_PENDING),
        ).rowcount
        if not changed:
            return False
        try:
            data = json.loads(req["noi_dung"] or "{}")
        except json.JSONDecodeError:
            data = {}
        conn.execute(
            "INSERT INTO Notifications (user_id, request_id, loai, tieu_de, noi_dung, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (req["user_id"], request_id, NOTI_REQUEST_APPROVED,
             _TITLES[req["loai_yeu_cau"]][NOTI_REQUEST_APPROVED],
             f"{ROLE_LABELS[0]} {admin['ho_ten']} đã duyệt: {_summary(req['loai_yeu_cau'], data)}",
             _now()),
        )
    return True


_SELECT = """
    SELECT n.id, n.request_id, n.loai, n.tieu_de, n.noi_dung, n.is_read, n.created_at,
           r.loai_yeu_cau, r.noi_dung AS request_data, r.trang_thai,
           r.created_at AS request_created_at,
           u.ho_ten AS sender_name, u.ma_giang_vien AS sender_code, u.role AS sender_role
    FROM Notifications n
    LEFT JOIN System_Requests r ON r.id = n.request_id
    LEFT JOIN Users u ON u.id = r.user_id
    WHERE n.user_id = ?
"""


def _to_dict(row) -> dict:
    item = dict(row)
    try:
        item["data"] = json.loads(item.pop("request_data") or "{}")
    except json.JSONDecodeError:
        item["data"] = {}
    return item


def get_unread_ids(user_id: int) -> list[int]:
    with _db() as conn:
        rows = conn.execute(
            "SELECT id FROM Notifications WHERE user_id = ? AND is_read = 0", (user_id,)
        ).fetchall()
    return [r["id"] for r in rows]


def mark_read(user_id: int, ids: list[int]) -> None:
    if not ids:
        return
    marks = ",".join("?" * len(ids))
    with _db() as conn:
        conn.execute(
            f"UPDATE Notifications SET is_read = 1 WHERE user_id = ? AND id IN ({marks})",
            [user_id, *ids],
        )


def list_notifications(user_id: int, limit: int = 30) -> list[dict]:
    with _db() as conn:
        rows = conn.execute(_SELECT + " ORDER BY n.id DESC LIMIT ?", (user_id, limit)).fetchall()
    return [_to_dict(r) for r in rows]


def get_notification(user_id: int, notification_id: int) -> dict | None:
    with _db() as conn:
        row = conn.execute(_SELECT + " AND n.id = ?", (user_id, notification_id)).fetchone()
    return _to_dict(row) if row else None


def _list_requests(user_code: str | None = None, request_type: str | None = None) -> list[dict]:
    """Lấy danh sách yêu cầu, kèm thông tin người gửi và nội dung đã giải mã."""
    sql = """
        SELECT
            r.id,
            r.user_id,
            r.loai_yeu_cau,
            r.noi_dung,
            r.trang_thai,
            r.created_at,
            u.ho_ten AS sender_name,
            u.ma_giang_vien AS sender_code
        FROM System_Requests r
        LEFT JOIN Users u ON u.id = r.user_id
        WHERE 1 = 1
    """
    params = []

    if user_code is not None:
        sql += " AND u.ma_giang_vien = ?"
        params.append(user_code)

    if request_type is not None:
        sql += " AND r.loai_yeu_cau = ?"
        params.append(request_type)

    sql += " ORDER BY r.id DESC"

    with _db() as conn:
        rows = conn.execute(sql, params).fetchall()

    records = []

    for row in rows:
        item = dict(row)

        try:
            data = json.loads(item.pop("noi_dung") or "{}")
        except (json.JSONDecodeError, TypeError):
            data = {}

        # Trạng thái trong System_Requests:
        # 0 = đang chờ xử lý, 1 = đã được duyệt.
        status = item.pop("trang_thai", STATUS_PENDING)

        item["status"] = (
            "pending" if status == STATUS_PENDING
            else "resolved" if status == STATUS_APPROVED
            else "unknown"
        )

        # Giữ nội dung gốc để thuận tiện tra cứu.
        item["request_data"] = data

        # Đưa các trường JSON thành cột để giao diện sử dụng.
        item.update(data)

        # Tạo tên cột thống nhất cho hai trang.
        item["request_type"] = item.pop("loai_yeu_cau")
        item["subject"] = (
            data.get("mon_thi")
            or data.get("loai_su_co")
            or ""
        )

        records.append(item)

    return records


def get_field_report_requests(user_code: str | None = None) -> list[dict]:
    """Lịch sử biên bản ca thi."""
    return _list_requests(
        user_code=user_code,
        request_type=REQUEST_FIELD_REPORT,
    )


def get_incident_requests(user_code: str | None = None) -> list[dict]:
    """Lịch sử báo cáo sự cố."""
    return _list_requests(
        user_code=user_code,
        request_type=REQUEST_INCIDENT,
    )

