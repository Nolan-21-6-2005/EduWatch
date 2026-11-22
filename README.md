# EduWatch VNUA

Ứng dụng giám sát phòng học/phòng thi, ghi nhận hành vi vi phạm bằng YOLO và quản lý nhật ký trên SQLite.

## Yêu cầu

- Python 3.10 trở lên.
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

## Camera: tải ảnh lên thay cho webcam

Dự án không còn mở webcam. Mỗi trong 4 khung camera nhận một ảnh do người dùng tải lên:

- Nhấp vào khung (hoặc kéo thả ảnh vào khung) để chọn ảnh JPG/PNG/WEBP/BMP, tối đa 10 MB. Nhấp lại để thay ảnh. Nút phóng to ở góc khung vẫn dùng để phóng to/toàn màn hình.
- Khung thứ i gắn với camera thứ i của phòng trong bảng `Cameras` (thiếu thì dùng camera đầu tiên), nên vi phạm được ghi đúng phòng.
- Ảnh được lưu trong bộ nhớ của backend (tối đa 64 ảnh, ảnh lớn được thu nhỏ còn cạnh dài 1280 px), nên chuyển trang vẫn còn ảnh nhưng **mất khi khởi động lại backend**.
- Khi bật AI, các khung được dự đoán **cùng lúc bằng một model** qua `src/services/detection_pipeline.py`: các khung gửi ảnh gần nhau (tối đa 4, cách nhau không quá ~80 ms) được gom thành một batch và chạy trong một lần predict. Khung hiển thị vẫn có tất cả bounding box; mỗi detection có độ tin cậy > 0,8 tạo một ảnh bằng chứng riêng chỉ có đúng bounding box đó và một bản ghi riêng trong `Violation_Logs`. Nhiều detection cùng nhãn trong một frame vẫn được duyệt và lưu độc lập, không gom theo tên nhãn. NMS dùng `iou=0.85`, `max_det=1000`, `agnostic_nms=False` để hạn chế loại nhầm các box cùng nhãn chồng lấn; NMS vẫn có thể loại box trùng lặp của cùng một đối tượng.
- Nhãn trên bounding box chỉ hiển thị tên lớp (ví dụ `phone`), không hiển thị xác suất. Confidence vẫn được giữ trong SQLite để phục vụ lọc ngưỡng, thống kê và xem chi tiết khi cần.
- Bằng chứng đi vào hàng đợi và **một luồng ghi log duy nhất** lưu lần lượt (FIFO) vào `Violation_Logs` kèm ảnh bằng chứng, nên thứ tự trong nhật ký đúng thứ tự hàng đợi. Tắt/bật lại AI không ghi trùng cho cùng một ảnh; muốn ghi lại hãy tải ảnh lại.
- `GET /camera/status` trả thêm `pipeline` (số ảnh/log đang chờ, số batch, kích thước batch gần nhất, số log đã ghi/bỏ qua) để theo dõi hàng đợi.
- API: `POST /camera/upload?camera_id=&slot=` (body là bytes ảnh), `GET /camera/frame?camera_id=&slot=&session=`.

## Bộ lọc

Mọi bộ lọc (Nhật ký vi phạm, Thống kê báo cáo, Xuất biên bản, Báo cáo sự cố) mặc định để trống/"Tất cả", nghĩa là truy xuất toàn bộ dữ liệu. Khoảng ngày chỉ được áp dụng khi người dùng chọn.

## Giới hạn trước khi triển khai thực tế

- Backend hiện chỉ nên chạy trên máy nội bộ (`127.0.0.1`). Các API quản trị, duyệt vi phạm và điều khiển camera chưa có middleware xác thực/phân quyền ở phía FastAPI; ẩn nút trên giao diện không thay thế được kiểm soát truy cập phía server.
- Mật khẩu hiện vẫn dùng SHA-256 không salt. Cần chuyển sang Argon2 hoặc PBKDF2 trước khi sử dụng với tài khoản thật.
- Chưa có ghi hình/phát video; `Cameras.video_source` trong SQLite không còn được dùng để mở nguồn.
- API tải ảnh lên cũng chưa có xác thực phía server (xem mục đầu tiên).
- Tài khoản tự đăng ký được tạo ở trạng thái `role = -1`, `status = 0`. Quản trị viên phải gán vai trò và mở khóa tài khoản trước khi người dùng đăng nhập.
