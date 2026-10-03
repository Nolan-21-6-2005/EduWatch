import sqlite3
import os
import hashlib
from pathlib import Path

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    db_dir = Path(__file__).resolve().parent / 'data_model'
    db_path = db_dir / 'eduwatch.db'

    db_dir.mkdir(parents=True, exist_ok=True)

    try:
        conn = sqlite3.connect(str(db_path))
        c = conn.cursor()
        c.execute("PRAGMA foreign_keys = ON;")

        # 1. Bang Users (Su dung ma_giang_vien lam dinh danh)
        c.execute('''CREATE TABLE IF NOT EXISTS Users 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            ma_giang_vien TEXT UNIQUE NOT NULL, 
            password TEXT NOT NULL, 
            role INTEGER NOT NULL, -- 0: Admin, 1: Giang vien, 2: Bao ve
            ho_ten TEXT NOT NULL,
            ngay_sinh TEXT, 
            gioi_tinh TEXT, 
            email TEXT UNIQUE,
            so_dien_thoai TEXT,
            anh_dai_dien TEXT DEFAULT 'data/avatars/default.png',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status INTEGER DEFAULT 1)''')

        # 2. Bang Buildings, Rooms, Cameras
        c.execute('''CREATE TABLE IF NOT EXISTS Buildings 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            ten_toa TEXT UNIQUE NOT NULL,
            is_deleted INTEGER DEFAULT 0)''')

        c.execute('''CREATE TABLE IF NOT EXISTS Rooms 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            building_id INTEGER NOT NULL, 
            ten_phong TEXT NOT NULL,
            is_deleted INTEGER DEFAULT 0,
            FOREIGN KEY(building_id) REFERENCES Buildings(id) ON DELETE CASCADE)''')

        c.execute('''CREATE TABLE IF NOT EXISTS Cameras
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            room_id INTEGER NOT NULL, 
            vi_tri_goc TEXT NOT NULL,
            video_source TEXT, 
            status INTEGER DEFAULT 1,
            FOREIGN KEY(room_id) REFERENCES Rooms(id) ON DELETE CASCADE)''')

        # 3. Bang Violation_Logs
        c.execute('''CREATE TABLE IF NOT EXISTS Violation_Logs
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            camera_id INTEGER, 
            loai_vi_pham TEXT NOT NULL, 
            session TEXT, 
            thoi_gian TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
            image_path TEXT, 
            confidence REAL, 
            is_confirmed INTEGER DEFAULT 0,
            review_status TEXT DEFAULT 'pending',
            FOREIGN KEY(camera_id) REFERENCES Cameras(id) ON DELETE SET NULL)''')

        # Tương thích với database cũ: bổ sung trạng thái duyệt nếu bảng đã tồn tại.
        columns = [row[1] for row in c.execute("PRAGMA table_info(Violation_Logs)").fetchall()]
        if "session" not in columns:
            c.execute("ALTER TABLE Violation_Logs ADD COLUMN session TEXT")
        if "review_status" not in columns:
            c.execute("ALTER TABLE Violation_Logs ADD COLUMN review_status TEXT DEFAULT 'pending'")

        # 4. Bang System_Requests
        c.execute('''CREATE TABLE IF NOT EXISTS System_Requests
            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER NOT NULL, 
            loai_yeu_cau TEXT, 
            noi_dung TEXT, 
            trang_thai INTEGER DEFAULT 0, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES Users(id))''')

        # Index toi uu
        c.execute("CREATE INDEX IF NOT EXISTS idx_rooms_building ON Rooms(building_id);")
        c.execute("CREATE INDEX IF NOT EXISTS idx_logs_time ON Violation_Logs(thoi_gian);")

        # Seed Data VNUA
        buildings = ["Cơ điện cũ", "Cơ điện mới", "Giảng đường A", "Giảng đường B", "Giảng đường C", "Nguyễn Đăng", "Giảng đường E"]
        for b_name in buildings:
            c.execute("INSERT OR IGNORE INTO Buildings (ten_toa) VALUES (?)", (f"Giảng đường {b_name}",))
            b_id = c.execute("SELECT id FROM Buildings WHERE ten_toa = ?", (f"Giảng đường {b_name}",)).fetchone()[0]
            
            for i in range(101, 104):
                room_name = f"P.{i}"
                c.execute("INSERT OR IGNORE INTO Rooms (building_id, ten_phong) VALUES (?, ?)", (b_id, room_name))
                r_id = c.execute("SELECT id FROM Rooms WHERE building_id=? AND ten_phong=?", (b_id, room_name)).fetchone()[0]
                
                cams = [(r_id, "Góc cửa chính"), (r_id, "Góc bàn giáo viên"), (r_id, "Góc cuối lớp"), (r_id, "Góc cửa phụ")]
                for cam in cams:
                    c.execute("INSERT OR IGNORE INTO Cameras (room_id, vi_tri_goc, video_source) VALUES (?, ?, ?)", 
                              (cam[0], cam[1], f"data/videos/sample_{i}.mp4"))

        # Không seed dữ liệu vi phạm giả.
        # Violation_Logs chỉ nhận dữ liệu từ pipeline phát hiện thật của backend.

        # Tai khoan mau voi Ma Giang Vien
        users = [
            ('AD001', hash_password('admin123'), 0, 'Nguyễn Hữu Quang Minh', '2003-01-01', 'Nam', 'minh.admin@vnua.edu.vn', '0912345678'),
            ('GV123', hash_password('gv123'), 1, 'Nguyễn Văn A', '1985-05-20', 'Nam', 'gv.a@vnua.edu.vn', '0987654321'),
            ('BV001', hash_password('bv123'), 2, 'Trần Thị B', '1990-10-15', 'Nữ', 'bv.b@vnua.edu.vn', '0123456789')
        ]
        c.executemany('''INSERT OR IGNORE INTO Users 
            (ma_giang_vien, password, role, ho_ten, ngay_sinh, gioi_tinh, email, so_dien_thoai) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', users)

        conn.commit()
        print(f"Hoan thanh khoi tao tai: {db_path}")

    except sqlite3.Error as e:
        print(f"Loi: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()