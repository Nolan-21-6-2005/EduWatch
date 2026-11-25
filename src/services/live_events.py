"""Bộ đếm phiên bản của nhật ký vi phạm để panel cập nhật theo thời gian thực.

Mỗi lần có log mới hoặc đổi trạng thái xác nhận, ``notify()`` tăng phiên bản. Panel hỏi
``/violations/live?since=<phiên bản>``; nếu chưa đổi thì backend trả ngay mà không truy vấn DB.
Phiên bản khởi tạo theo thời gian để sau khi backend khởi động lại, client cũ tự tải lại dữ liệu.
"""
import threading
import time

_lock = threading.Lock()
_version = time.time_ns() // 1000


def notify() -> int:
    global _version
    with _lock:
        _version += 1
        return _version


def version() -> int:
    return _version
