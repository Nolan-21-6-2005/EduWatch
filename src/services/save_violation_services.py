from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = BASE_DIR / "data_model" / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

def _save_violation(
    label: str, 
    confidence: float, 
    frame, 
    camera_id: int | None, 
    session: str
):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    image_path = EVIDENCE_DIR / f"detection_{timestamp}.jpg"
    if not cv2.imwrite(str(image_path), frame):
        image_path = None

    with sqlite3.connect(getdatabase_path()) as conn:
        cursor = conn.execute(
            """
            INSERT INTO Violation_Logs
            (camera_id, loai_vi_pham, thoi_gian, session, image_path, confidence, is_confirmed, review_status)
            VALUES (?, ?, ?, ?, ?, ?, 0, 'pending')
            """,
            (
                camera_id,
                label,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                session,
                str(image_path.relative_to(BASE_DIR)) if image_path else None,
                confidence,
            ),
        )
        conn.commit()
        return cursor.lastrowid

