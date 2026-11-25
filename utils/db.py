"""Kết nối SQLite dùng chung, an toàn trên Windows.

- ``with sqlite3.connect(...)`` chỉ commit chứ KHÔNG đóng kết nối. Trên Windows file .db vẫn bị
  khóa cho tới khi bộ thu gom rác đóng nó, gây lỗi "database is locked" khi luồng ghi log và
  các request đọc chạy cùng lúc. ``connect()`` luôn đóng kết nối sau khi dùng.
- Chế độ WAL cho phép đọc (panel log thời gian thực) song song với ghi (luồng lưu vi phạm).
"""
from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager

from utils.helper import getdatabase_path

_BUSY_TIMEOUT_S = 30
_wal_lock = threading.Lock()
_wal_ready = False


def open_connection(*, row_factory=None, foreign_keys: bool = False) -> sqlite3.Connection:
    """Mở kết nối đã cấu hình (người gọi tự đóng). Ưu tiên dùng ``connect()``."""
    global _wal_ready
    conn = sqlite3.connect(str(getdatabase_path()), timeout=_BUSY_TIMEOUT_S)
    conn.execute(f"PRAGMA busy_timeout = {_BUSY_TIMEOUT_S * 1000}")
    if not _wal_ready:
        with _wal_lock:
            if not _wal_ready:
                try:
                    conn.execute("PRAGMA journal_mode = WAL")
                except sqlite3.DatabaseError:
                    pass  # ví dụ ổ đĩa mạng/chỉ đọc: giữ chế độ mặc định
                _wal_ready = True
    conn.execute("PRAGMA synchronous = NORMAL")
    if foreign_keys:
        conn.execute("PRAGMA foreign_keys = ON")
    if row_factory is not None:
        conn.row_factory = row_factory
    return conn


@contextmanager
def connect(*, row_factory=None, foreign_keys: bool = False):
    """Tự commit khi thành công, rollback khi lỗi và luôn đóng kết nối."""
    conn = open_connection(row_factory=row_factory, foreign_keys=foreign_keys)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def ensure_runtime_setup() -> None:
    """Gọi một lần khi backend khởi động: bật WAL và tạo chỉ mục cho truy vấn nhật ký."""
    with connect() as conn:
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_logs_time ON Violation_Logs(thoi_gian)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_logs_label ON Violation_Logs(loai_vi_pham)"
        )
