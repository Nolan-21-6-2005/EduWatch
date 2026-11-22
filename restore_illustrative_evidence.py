"""Gắn ảnh minh họa có bounding box cho các log đang thiếu ảnh.

Ảnh trong thư mục data_model/evidence/illustrative_*.jpg là ảnh minh họa,
không phải ảnh camera thật và không được dùng làm bằng chứng kỷ luật thực tế.
Chỉ các dòng thiếu ảnh hoặc trỏ tới file không còn tồn tại mới được cập nhật.
"""
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data_model" / "eduwatch.db"
EVIDENCE_DIR = BASE_DIR / "data_model" / "evidence"

IMAGE_BY_LABEL = {
    "Ngủ gật": "illustrative_ngu_gat.jpg",
    "Cúi người sâu": "illustrative_cui_nguoi_sau.jpg",
    "Rời vị trí": "illustrative_roi_vi_tri.jpg",
    "Sử dụng điện thoại": "illustrative_su_dung_dien_thoai.jpg",
    "Quay bài/Trao đổi": "illustrative_quay_bai_trao_doi.jpg",
    "Đứng dậy": "illustrative_dung_day.jpg",
    "Đọc tài liệu": "illustrative_doc_tai_lieu.jpg",
    "Di chuyển": "illustrative_di_chuyen.jpg",
}


def main():
    if not DB_PATH.is_file():
        raise FileNotFoundError(f"Không tìm thấy database: {DB_PATH}")

    for filename in IMAGE_BY_LABEL.values():
        path = EVIDENCE_DIR / filename
        if not path.is_file():
            raise FileNotFoundError(f"Thiếu ảnh minh họa: {path}")

    updated = {}
    skipped_with_image = 0
    unknown_labels = {}

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        rows = conn.execute(
            "SELECT id, loai_vi_pham, image_path FROM Violation_Logs ORDER BY id"
        ).fetchall()

        for row_id, label, current_path in rows:
            # Giữ nguyên ảnh thật nếu đường dẫn hiện tại vẫn tồn tại.
            if current_path:
                candidate = Path(str(current_path))
                if not candidate.is_absolute():
                    candidate = BASE_DIR / candidate
                if candidate.is_file():
                    skipped_with_image += 1
                    continue

            filename = IMAGE_BY_LABEL.get(str(label or "").strip())
            if not filename:
                unknown_labels[str(label or "(trống)")] = unknown_labels.get(
                    str(label or "(trống)"), 0
                ) + 1
                continue

            relative_path = (Path("data_model") / "evidence" / filename).as_posix()
            conn.execute(
                "UPDATE Violation_Logs SET image_path = ? WHERE id = ?",
                (relative_path, row_id),
            )
            updated[str(label)] = updated.get(str(label), 0) + 1

        conn.commit()

    print(f"Đã cập nhật: {sum(updated.values())} log")
    for label, count in sorted(updated.items()):
        print(f"  {label}: {count}")
    print(f"Giữ nguyên log đã có ảnh hợp lệ: {skipped_with_image}")
    if unknown_labels:
        print("Nhãn chưa có ảnh minh họa (được giữ nguyên):")
        for label, count in sorted(unknown_labels.items()):
            print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
