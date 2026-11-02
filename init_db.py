import hashlib
import sqlite3
from pathlib import Path

from src.database_query.notifications import ensure_schema as ensure_notification_schema


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def init_db() -> None:
    db_dir = Path(__file__).resolve().parent / "data_model"
    db_path = db_dir / "eduwatch.db"
    db_dir.mkdir(parents=True, exist_ok=True)

    conn = None
    try:
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_giang_vien TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role INTEGER NOT NULL,
                ho_ten TEXT NOT NULL,
                ngay_sinh TEXT,
                gioi_tinh TEXT,
                email TEXT UNIQUE,
                so_dien_thoai TEXT,
                anh_dai_dien TEXT DEFAULT 'data_model/avatar/default.png',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status INTEGER DEFAULT 1
            )"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Buildings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten_toa TEXT UNIQUE NOT NULL,
                is_deleted INTEGER DEFAULT 0
            )"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_id INTEGER NOT NULL,
                ten_phong TEXT NOT NULL,
                is_deleted INTEGER DEFAULT 0,
                monitor_mode INTEGER DEFAULT 0,
                FOREIGN KEY(building_id) REFERENCES Buildings(id) ON DELETE CASCADE
            )"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Cameras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                vi_tri_goc TEXT NOT NULL,
                video_source TEXT,
                status INTEGER DEFAULT 1,
                FOREIGN KEY(room_id) REFERENCES Rooms(id) ON DELETE CASCADE
            )"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS Violation_Logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                camera_id INTEGER,
                loai_vi_pham TEXT NOT NULL,
                session TEXT,
                thoi_gian TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                confidence REAL,
                is_confirmed INTEGER DEFAULT 0,
                review_status TEXT DEFAULT 'pending',
                FOREIGN KEY(camera_id) REFERENCES Cameras(id) ON DELETE SET NULL
            )"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS System_Requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                loai_yeu_cau TEXT,
                noi_dung TEXT,
                trang_thai INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES Users(id)
            )"""
        )

        # Migrate columns used by the current application when opening an older DB.
        room_columns = {
            row[1] for row in cursor.execute("PRAGMA table_info(Rooms)").fetchall()
        }
        if "monitor_mode" not in room_columns:
            cursor.execute("ALTER TABLE Rooms ADD COLUMN monitor_mode INTEGER DEFAULT 0")

        log_columns = {
            row[1] for row in cursor.execute("PRAGMA table_info(Violation_Logs)").fetchall()
        }
        if "session" not in log_columns:
            cursor.execute("ALTER TABLE Violation_Logs ADD COLUMN session TEXT")
        if "review_status" not in log_columns:
            cursor.execute(
                "ALTER TABLE Violation_Logs ADD COLUMN review_status TEXT DEFAULT 'pending'"
            )
        if "is_confirmed" not in log_columns:
            cursor.execute(
                "ALTER TABLE Violation_Logs ADD COLUMN is_confirmed INTEGER DEFAULT 0"
            )

        # These constraints make the seed operations idempotent.
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_rooms_building_name "
            "ON Rooms(building_id, ten_phong)"
        )
        cursor.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_cameras_room_position "
            "ON Cameras(room_id, vi_tri_goc)"
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rooms_building ON Rooms(building_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_time ON Violation_Logs(thoi_gian)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_logs_review_session "
            "ON Violation_Logs(review_status, session)"
        )

        ensure_notification_schema(conn)

        # Names match the values stored in Buildings.ten_toa.
        buildings = [
            "Giảng đường Cơ điện cũ",
            "Giảng đường Cơ điện mới",
            "Giảng đường A",
            "Giảng đường B",
            "Giảng đường C",
            "Nguyễn Đăng",
            "Giảng đường E",
        ]
        for building_name in buildings:
            cursor.execute(
                "INSERT OR IGNORE INTO Buildings (ten_toa, is_deleted) VALUES (?, 0)",
                (building_name,),
            )
            building_row = cursor.execute(
                "SELECT id FROM Buildings WHERE ten_toa = ?", (building_name,)
            ).fetchone()
            building_id = int(building_row[0])

            for room_number in range(101, 104):
                room_name = f"P.{room_number}"
                cursor.execute(
                    "INSERT OR IGNORE INTO Rooms "
                    "(building_id, ten_phong, is_deleted, monitor_mode) VALUES (?, ?, 0, 0)",
                    (building_id, room_name),
                )
                room_row = cursor.execute(
                    "SELECT id FROM Rooms WHERE building_id = ? AND ten_phong = ?",
                    (building_id, room_name),
                ).fetchone()
                room_id = int(room_row[0])

                cameras = [
                    ("Góc cửa chính", f"data/videos/sample_{room_number}.mp4"),
                    ("Góc bàn giáo viên", f"data/videos/sample_{room_number}.mp4"),
                    ("Góc cuối lớp", f"data/videos/sample_{room_number}.mp4"),
                    ("Góc cửa phụ", f"data/videos/sample_{room_number}.mp4"),
                ]
                for position, source in cameras:
                    cursor.execute(
                        "INSERT OR IGNORE INTO Cameras "
                        "(room_id, vi_tri_goc, video_source, status) VALUES (?, ?, ?, 1)",
                        (room_id, position, source),
                    )

        sample_users = [
            (
                "AD001", hash_password("admin123"), 0,
                "Nguyễn Hữu Quang Minh", "2003-01-01", "Nam",
                "minh.admin@vnua.edu.vn", "0912345678",
            ),
            (
                "GV123", hash_password("gv123"), 1,
                "Nguyễn Văn A", "1985-05-20", "Nam",
                "gv.a@vnua.edu.vn", "0987654321",
            ),
            (
                "BV001", hash_password("bv123"), 2,
                "Trần Thị B", "1990-10-15", "Nữ",
                "bv.b@vnua.edu.vn", "0123456789",
            ),
        ]
        cursor.executemany(
            """INSERT OR IGNORE INTO Users
                (ma_giang_vien, password, role, ho_ten, ngay_sinh, gioi_tinh,
                 email, so_dien_thoai)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            sample_users,
        )

        conn.commit()
        print(f"Hoàn thành khởi tạo cơ sở dữ liệu: {db_path}")
    except sqlite3.Error:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    init_db()
