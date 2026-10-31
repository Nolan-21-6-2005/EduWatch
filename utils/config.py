import cv2
import numpy as np
from pathlib import Path

# Thư mục gốc của project Stable
BASE_DIR = Path(__file__).resolve().parents[1]

# Thư mục chứa dữ liệu của project
DATA_DIR = BASE_DIR / "data_model"

# Thư mục avatar
AVATAR_DIR = DATA_DIR / "avatar"

# Database
DATABASE_PATH = DATA_DIR / "eduwatch.db"


# Đảm bảo thư mục avatar tồn tại
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

# Tên hiển thị đầy đủ cho từng giảng đường (giá trị lưu trong session_state giữ nguyên).
BUILDING_NAMES = {
    "Giảng đường ND": "Giảng đường Nguyễn Đăng",
}

SESSION_MAP = {
    "Phòng thi": "exam",
    "Phòng thường": "study",
}

statuses = {
    "pending": "Chờ xác nhận",
    "confirmed": "Đã xác nhận",
    "wrong": "Báo sai AI",
}

latest_detections = []
last_detect_time = {}
is_running = True
is_active = False

COOLDOWN = 5

# Màu xám tối (#2b2b2b)
placeholder_frame = np.ones((480, 640, 3), dtype=np.uint8) * 43 
cv2.putText(placeholder_frame, "CAMERA IS OFF", (160, 250), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2, cv2.LINE_AA)
            
admin_logo_path = "view/asset/admin.png"
supervision_logo_path = "view/asset/supervision.png"
security_logo_path = "view/asset/security.png"

css_files = [
    "view/style/global.css",
    "view/style/detector.css",
    "view/style/auth.css",
    "view/style/profile.css",
]
