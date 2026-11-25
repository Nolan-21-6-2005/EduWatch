from datetime import datetime
from pathlib import Path

import cv2

from src.services import live_events
from utils.config import AUTO_SUBMIT_THRESHOLD, LOG_CONF_THRESHOLD
from utils.db import connect as db_connect

BASE_DIR = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = BASE_DIR / "data_model" / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def _write_image(path: Path, frame) -> bool:
    """Ghi JPEG qua imencode + write_bytes: cv2.imwrite không ghi được vào đường dẫn có
    ký tự Unicode (ví dụ thư mục "Dự án") trên Windows."""
    try:
        ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        if not ok:
            return False
        path.write_bytes(buffer.tobytes())
        return True
    except OSError:
        return False


def _save_violation(
    label: str,
    confidence: float,
    frame,
    camera_id: int | None,
    session: str,
):
    # < 0.6: không ghi log; 0.6 <= conf < 0.85: ghi log chờ xác nhận; >= 0.85: tự động submit.
    if float(confidence) < LOG_CONF_THRESHOLD:
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    image_path = EVIDENCE_DIR / f"detection_{timestamp}.jpg"
    if not _write_image(image_path, frame):
        image_path = None

    is_confirmed = 1 if float(confidence) >= AUTO_SUBMIT_THRESHOLD else 0
    review_status = "confirmed" if is_confirmed else "pending"
    with db_connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO Violation_Logs
            (camera_id, loai_vi_pham, thoi_gian, session, image_path, confidence, is_confirmed, review_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                camera_id,
                label,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                session,
                # as_posix: lưu dấu "/" để đường dẫn dùng được trên cả Windows lẫn Linux.
                image_path.relative_to(BASE_DIR).as_posix() if image_path else None,
                confidence,
                is_confirmed,
                review_status,
            ),
        )
        row_id = cursor.lastrowid
    live_events.notify()  # sau khi commit: panel log nhận log mới ngay
    return row_id
