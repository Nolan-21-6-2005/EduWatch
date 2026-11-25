import os
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


# Địa chỉ backend FastAPI. Dùng 127.0.0.1 thay vì "localhost": trên Windows "localhost" thường
# được phân giải sang IPv6 (::1) trước, trong khi uvicorn chỉ lắng nghe IPv4 -> mỗi request
# bị trễ ~1-2 giây trước khi quay lại IPv4.
API_HOST = os.getenv("EDUWATCH_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("EDUWATCH_API_PORT", "8000"))
API_BASE = f"http://{API_HOST}:{API_PORT}"

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
# Model hiện tại (AI_model/yolo_eduwatch.pt) có đúng 8 lớp theo bảng 8 sự kiện bắt lỗi tự động.
# Lớp model trả về mà không có trong bảng này (ví dụ "leaning_down" của model cũ) bị bỏ qua:
# không vẽ, không ghi log. Tên tiếng Việt để hiển thị nằm ở utils/labels_vi.py.
VIOLATION_LABELS = {
    "sleeping": "sleeping",
    "eating": "eating",
    "leave_seat": "leaving_seat", "leaving_seat": "leaving_seat",
    "phone": "phone",
    "turning_head": "turning_head",
    "standing": "standing",
    "reading": "reading",
    "moving": "walking", "walking": "walking",
}

# 8 sự kiện theo bảng: nhãn -> áp dụng cho phòng nào ("both" = cả hai loại phòng).
VIOLATION_SCOPE = {
    "sleeping": "both",       # 1. Ngủ gật
    "eating": "both",         # 2. Ăn uống
    "leaving_seat": "both",   # 3. Rời vị trí
    "phone": "exam",          # 4. Sử dụng điện thoại
    "turning_head": "exam",   # 5. Quay bài/Trao đổi
    "standing": "exam",       # 6. Đứng dậy
    "reading": "exam",        # 7. Đọc tài liệu
    "walking": "exam",        # 8. Di chuyển
}

# session ("study" = phòng thường, "exam" = phòng thi) -> tập nhãn được nhận diện và hiển thị log.
SESSION_LABELS = {
    "study": frozenset(k for k, v in VIOLATION_SCOPE.items() if v in ("both", "study")),
    "exam": frozenset(VIOLATION_SCOPE),  # phòng thi: tất cả 8 sự kiện
}

# Ngưỡng độ chính xác:
#   conf >= LOG_CONF_THRESHOLD      -> ghi log (trạng thái chờ xác nhận)
#   conf >= AUTO_SUBMIT_THRESHOLD   -> ghi log và tự động submit (xác nhận)
LOG_CONF_THRESHOLD = 0.6
AUTO_SUBMIT_THRESHOLD = 0.85

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
