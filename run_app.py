"""Chạy cả backend (FastAPI) và giao diện (Streamlit) bằng một lệnh: python run_app.py

Tối ưu cho Windows:
- Không dùng --reload của uvicorn (tiến trình theo dõi file nạp lại model YOLO/torch mỗi lần lưu file).
- Ép UTF-8 cho tiến trình con để in tiếng Việt không lỗi.
- Chờ backend sẵn sàng rồi mới mở trình duyệt; Ctrl+C dừng cả hai tiến trình.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from utils.config import API_HOST, API_PORT  # noqa: E402

UI_PORT = int(os.getenv("EDUWATCH_UI_PORT", "8501"))


def _wait_port(host: str, port: int, timeout: float = 120.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def main() -> int:
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend_app:app",
         "--host", API_HOST, "--port", str(API_PORT)],
        cwd=ROOT, env=env,
    )
    frontend = None
    try:
        if not _wait_port(API_HOST, API_PORT):
            print("Backend không khởi động được.")
            return 1
        frontend = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "frontend_app.py",
             "--server.port", str(UI_PORT), "--server.headless", "true"],
            cwd=ROOT, env=env,
        )
        if _wait_port("127.0.0.1", UI_PORT):
            webbrowser.open(f"http://localhost:{UI_PORT}")
        print("Đang chạy. Nhấn Ctrl+C để dừng.")
        while backend.poll() is None and frontend.poll() is None:
            time.sleep(1)
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        for proc in (frontend, backend):
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
