# EduWatch VNUA

Ứng dụng giám sát phòng học/phòng thi, ghi nhận hành vi vi phạm bằng YOLO và quản lý nhật ký trên SQLite.

## Yêu cầu

- Python 3.10 trở lên.
- Camera USB hoặc nguồn video được cấu hình cho backend.
- File trọng số `AI_model/yolo_eduwatch.pt`.
- Cơ sở dữ liệu `data_model/eduwatch.db`.

## Cài đặt

Tạo môi trường ảo và cài các thư viện:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Chạy ứng dụng

Mở hai terminal tại thư mục gốc project.

Terminal 1 — FastAPI:

```bash
uvicorn backend_app:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 2 — Streamlit:

```bash
streamlit run frontend_app.py
```

Mặc định giao diện Streamlit chạy tại `http://localhost:8501`, API chạy tại `http://localhost:8000`.

## Cấu trúc chính

```text
AI_model/              # YOLO weights
data_model/            # SQLite, avatar, evidence
src/backend/           # FastAPI routers
src/database_query/    # SQL queries
src/frontend/          # Streamlit-to-API services
src/services/          # Camera and persistence services
view/asset/            # HTML/JavaScript assets
view/component/        # Reusable UI components
view/pages/            # Streamlit pages
view/style/             # CSS
utils/                  # Shared configuration/helpers
```

## Lưu ý về camera

Hiện tại backend chỉ mở một nguồn camera cục bộ bằng `cv2.VideoCapture(0)`. Các trường `Cameras.video_source` trong SQLite chưa được nối vào bộ đọc luồng; ba ô camera phụ được hiển thị là chưa kết nối thay vì giả trạng thái trực tiếp. Muốn chạy nhiều camera độc lập, cần cấu hình nguồn video/RTSP thực tế và triển khai bộ quản lý luồng theo `camera_id`.

Các đường dẫn `data/videos/sample_*.mp4` có trong dữ liệu mẫu phải trỏ tới file tồn tại trước khi sử dụng làm nguồn video.

## Giới hạn trước khi triển khai thực tế

- Backend hiện chỉ nên chạy trên máy nội bộ (`127.0.0.1`). Các API quản trị, duyệt vi phạm và điều khiển camera chưa có middleware xác thực/phân quyền ở phía FastAPI; ẩn nút trên giao diện không thay thế được kiểm soát truy cập phía server.
- Mật khẩu hiện vẫn dùng SHA-256 không salt. Cần chuyển sang Argon2 hoặc PBKDF2 trước khi sử dụng với tài khoản thật.
- Chức năng ghi hình video chưa được triển khai. Nút trong thanh điều khiển hiện chỉ tạm dừng/tiếp tục luồng hiển thị.
- Chức năng nhiều camera độc lập chưa hoàn thiện; `video_source` trong SQLite chưa được sử dụng để mở từng nguồn.
- Tài khoản tự đăng ký được tạo ở trạng thái `role = -1`, `status = 0`. Quản trị viên phải gán vai trò và mở khóa tài khoản trước khi người dùng đăng nhập.
