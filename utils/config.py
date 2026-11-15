from collections import deque
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
    "Nguyễn Đăng": "Giảng đường Nguyễn Đăng",
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

# Nhãn của model -> nhãn vi phạm lưu vào nhật ký và vẽ trên khung camera.
# Lớp không có trong bảng (ví dụ "reading") là hành vi bình thường: không vẽ, không ghi log.
# Model đã dùng sẵn tên mới (leaving_seat, leaning_down, walking) cũng được nhận.
VIOLATION_LABELS = {
    "phone": "phone",
    "leave_seat": "leaving_seat", "leaving_seat": "leaving_seat",
    "turning_head": "turning_head",
    "head_down": "leaning_down", "leaning_down": "leaning_down",
    "sleeping": "sleeping",
    "standing": "standing",
    "moving": "walking", "walking": "walking",
}

latest_detections = deque(maxlen=100)
# Bật/tắt nhận diện AI cho các ảnh được tải lên khung camera.
is_active = False

admin_logo_path = "view/asset/hoc_vien.png"
supervision_logo_path = "view/asset/giang_vien.png"
security_logo_path = "view/asset/bao_ve.png"

css_files = [
    "view/style/global.css",
    "view/style/detector.css",
    "view/style/camera.css",
    "view/style/auth.css",
    "view/style/profile.css",
]
