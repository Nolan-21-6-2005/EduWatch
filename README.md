# EduWatch VNUA

Hệ thống giám sát phòng học / phòng thi tại Học viện Nông nghiệp Việt Nam. Ứng dụng dùng mô hình YOLO để
nhận diện tự động **8 hành vi vi phạm**, ghi nhật ký kèm ảnh bằng chứng vào SQLite và cho phép giám sát viên
xác nhận hoặc báo sai theo thời gian thực. Giao diện Streamlit, backend FastAPI.

- Tài liệu này mô tả đúng trạng thái hiện tại của project.
- Lịch sử thay đổi nằm ở [`logs/CHANGELOG.md`](logs/CHANGELOG.md).

## Mục lục

1. [Mục tiêu đã đạt được](#1-mục-tiêu-đã-đạt-được)
2. [Hạn chế hiện tại](#2-hạn-chế-hiện-tại)
3. [Tính năng theo vai trò](#3-tính-năng-theo-vai-trò)
4. [Nhận diện AI](#4-nhận-diện-ai)
5. [Kiến trúc và cấu trúc thư mục](#5-kiến-trúc-và-cấu-trúc-thư-mục)
6. [Cài đặt và chạy](#6-cài-đặt-và-chạy)
7. [Cấu hình](#7-cấu-hình)
8. [Cơ sở dữ liệu và dữ liệu mẫu](#8-cơ-sở-dữ-liệu-và-dữ-liệu-mẫu)
9. [API chính](#9-api-chính)
10. [Sử dụng camera (tải ảnh lên)](#10-sử-dụng-camera-tải-ảnh-lên)
11. [Hướng phát triển](#11-hướng-phát-triển)

---

## 1. Mục tiêu đã đạt được

**Nhận diện và ghi log**

- [x] Mô hình YOLO `AI_model/yolo_eduwatch.pt` nhận diện 8 lớp: `sleeping`, `eating`, `leaving_seat`, `phone`, `turning_head`, `standing`, `reading`, `walking`, tương ứng bảng 8 sự kiện bắt lỗi tự động.
- [x] Phân biệt **Phòng thường** và **Phòng thi** bằng bộ chọn trên trang Giám sát: phòng thường chỉ nhận diện và hiển thị 3 lỗi dùng chung, phòng thi nhận diện và hiển thị cả 8 lỗi.
- [x] Ngưỡng độ chính xác: từ **0,6** thì ghi log (chờ xác nhận), từ **0,85** thì tự động xác nhận (submit).
- [x] Một ảnh có nhiều lỗi thì ghi **từng log riêng**; mỗi log có ảnh bằng chứng riêng chỉ chứa đúng một bounding box. Hai đối tượng cùng nhãn vẫn là hai log.
- [x] Nhãn trên bounding box và trong mọi màn hình hiển thị đều là **tiếng Việt** (có dấu; tự chuyển không dấu nếu máy không có font phù hợp).
- [x] Dự đoán 4 khung camera cùng lúc bằng một lần `predict` (batch), có hàng đợi ghi log một luồng nên thứ tự log đúng thứ tự phát hiện.

**Giám sát và nhật ký**

- [x] Nhật ký vi phạm cập nhật **thời gian thực** (độ trễ khoảng 1 giây), chỉ thêm/sửa đúng thẻ thay đổi, lọc theo loại phòng đang chọn.
- [x] Trang Nhật ký vi phạm có bộ lọc theo ngày, tòa nhà/phòng, chế độ, loại vi phạm, trạng thái; xuất CSV.
- [x] Thống kê báo cáo cho quản trị viên: KPI theo phòng thi/phòng thường, biểu đồ cột loại vi phạm đã xác nhận.

**Hệ thống**

- [x] Ba vai trò (Học viện/Admin, Giảng viên, Bảo vệ) với menu và quyền xem riêng; thanh tìm kiếm trang trên topbar.
- [x] Quản lý tòa nhà, phòng, camera và người dùng (gán vai trò, khóa/mở khóa, đặt lại mật khẩu).
- [x] Luồng biên bản (giảng viên) và báo cáo sự cố (bảo vệ) có thông báo và duyệt bởi quản trị viên.
- [x] Chạy ổn trên Windows: một lệnh khởi động cả hai tiến trình, tự dùng GPU nếu có, SQLite không bị khóa, xử lý đường dẫn có dấu tiếng Việt.

> Chưa có số liệu đánh giá định lượng (mAP, precision, recall theo từng lớp và từng góc camera) trong repo.
> Mục tiêu tiếp theo là bổ sung bảng số liệu này sau mỗi lần huấn luyện lại.

## 2. Hạn chế hiện tại

### 2.1. Dữ liệu huấn luyện và góc camera (hạn chế lớn nhất)

Dataset hiện tại **chỉ đủ tốt cho hai góc quay: đầu phòng và cuối phòng**. Các góc quay khác cho kết quả
nhận diện kém (bỏ sót hoặc nhận nhầm hành vi).

Trong CSDL, mỗi phòng có 4 góc camera: *Góc bàn giáo viên* (đầu phòng), *Góc cuối lớp* (cuối phòng),
*Góc cửa chính* và *Góc cửa phụ*. Hiện chỉ nên tin kết quả từ góc đầu phòng và cuối phòng.

Hệ quả khi vận hành:

- Log từ các góc còn lại có độ tin cậy thấp hơn thực tế dù model trả về confidence cao; **giám sát viên nên xem lại ảnh bằng chứng** thay vì dựa hoàn toàn vào tự động xác nhận (≥ 0,85).
- Chưa có lựa chọn "chỉ chạy AI cho góc đã được kiểm chứng"; hệ thống đang chạy AI cho mọi khung.
- Các lỗi dựa nhiều vào tư thế (ngủ gật, quay bài, đứng dậy, rời vị trí) phụ thuộc góc nhìn nhiều hơn các lỗi dựa vào đồ vật (điện thoại, tài liệu).

### 2.2. Hạn chế về mô hình và nhận diện

- Chưa có đánh giá định lượng theo từng góc camera và từng loại phòng (xem mục 1).
- Kích thước suy luận `IMGSZ = 320` (trong `src/services/camera_services.py`) ưu tiên tốc độ trên CPU; đối tượng nhỏ hoặc ở xa có thể bị bỏ sót. Chưa thử nghiệm các kích thước lớn hơn.
- YOLO trả về box sau NMS (`iou=0,85`, `max_det=1000`). Ứng dụng lưu độc lập mọi box được trả về, nhưng không khôi phục được box mà NMS đã loại; IoU cao có thể sinh box trùng cho cùng một đối tượng.
- Nhận diện theo từng ảnh riêng lẻ, chưa xét chuỗi thời gian (ví dụ "ngủ gật" cần kéo dài > 15 giây, "đứng dậy" cần so với mặt bằng chung theo thời gian làm bài). Ngưỡng thời gian trong bảng mô tả sự kiện chưa được áp dụng.

### 2.3. Hạn chế về hệ thống

- **Chưa có video/luồng camera thật**: mỗi khung nhận một ảnh do người dùng tải lên. Cột `Cameras.video_source` không còn được dùng.
- Ảnh tải lên lưu trong bộ nhớ backend (tối đa 64 ảnh) nên **mất khi khởi động lại backend**.
- Hàng đợi ghi log tối đa 256 bằng chứng; đầy thì bỏ qua và đếm vào `dropped`.
- API FastAPI **chưa có xác thực/phân quyền phía server** (các API quản trị, duyệt vi phạm, tải ảnh lên). Ẩn nút trên giao diện không thay thế kiểm soát truy cập. Chỉ chạy backend ở `127.0.0.1` trên máy nội bộ.
- Mật khẩu dùng SHA-256 không salt; cần chuyển sang Argon2 hoặc PBKDF2 trước khi dùng với tài khoản thật.
- Tài khoản tự đăng ký được tạo ở trạng thái chờ (`role = -1`, `status = 0`); quản trị viên phải gán vai trò và mở khóa.
- Thanh tìm kiếm trang lọc theo chữ có dấu (gõ "giam" không ra "Giám sát").
- Trang Nhật ký vi phạm (đầy đủ) và trang Thống kê chưa tự cập nhật theo thời gian thực (chỉ panel nhật ký ở trang Giám sát).
- Chưa có bộ kiểm thử tự động; các thay đổi được kiểm tra bằng script mô phỏng và chạy tay.

### 2.4. Dữ liệu mẫu lẫn với dữ liệu thật

Database kèm theo chứa nhiều log mẫu (nhãn tiếng Việt, ảnh `illustrative_*.jpg` có watermark **ẢNH MINH HỌA**) trộn với log do model ghi
(nhãn tiếng Anh như `sleeping`, `phone`). Số liệu thống kê hiện tại vì vậy **không phản ánh độ chính xác của model**. Xem mục 8.

## 3. Tính năng theo vai trò

| Vai trò | `role` | Trang |
|---|---|---|
| Học viện (Admin) | 0 | Thống kê báo cáo, Giám sát trực tiếp, Nhật ký vi phạm, Danh sách tòa nhà (thêm/sửa/kích hoạt), Quản lý người dùng |
| Giảng viên | 1 | Giám sát trực tiếp (bật AI, chọn Phòng thi/Phòng thường), Nhật ký vi phạm, Xuất biên bản |
| Bảo vệ | 2 | Giám sát an ninh (chỉ xem), Danh sách tòa nhà (chỉ xem), Báo cáo sự cố |

Tất cả vai trò có trang **Thông tin cá nhân** (mở từ sidebar hoặc thanh tìm kiếm) và chuông **thông báo**.
Điều hướng khai báo duy nhất trong `view/navigation.py` bằng `st.navigation()`; danh sách trang đổi theo `role`.

Ghi chú: công tắc bật AI, bộ chọn Phòng thi/Phòng thường và các nút **Xác nhận / Báo sai** ở panel nhật ký chỉ có ở trang
Giám sát của giảng viên; trang camera của Admin và Bảo vệ chỉ xem. Quyền duyệt biên bản/sự cố do `approve_request()` kiểm tra `role = 0`.

## 4. Nhận diện AI

### 4.1. Tám sự kiện và phạm vi áp dụng

| TT | Nhãn model | Tên hiển thị | Phòng thường | Phòng thi |
|---|---|---|:---:|:---:|
| 1 | `sleeping` | Ngủ gật | ✓ | ✓ |
| 2 | `eating` | Ăn uống | ✓ | ✓ |
| 3 | `leaving_seat` | Rời vị trí | ✓ | ✓ |
| 4 | `phone` | Sử dụng điện thoại | | ✓ |
| 5 | `turning_head` | Quay bài/Trao đổi | | ✓ |
| 6 | `standing` | Đứng dậy | | ✓ |
| 7 | `reading` | Đọc tài liệu | | ✓ |
| 8 | `walking` | Di chuyển | | ✓ |

- Phạm vi nằm trong `VIOLATION_SCOPE` và `SESSION_LABELS` ở `utils/config.py`.
- Tên tiếng Việt nằm trong `VIOLATION_NAMES_VI` ở `utils/labels_vi.py`. CSDL và logic nội bộ luôn dùng nhãn tiếng Anh chuẩn; chỉ khi hiển thị mới dịch bằng `vi_label()`.
- Lớp mà model trả về nhưng không có trong bảng sẽ bị bỏ qua (không vẽ, không ghi log). Log cũ như `leaning_down` / "Cúi người sâu" vẫn hiển thị bình thường.

### 4.2. Ngưỡng độ chính xác

| Confidence | Kết quả |
|---|---|
| < 0,6 | Bỏ qua: không vẽ box, không ghi log |
| 0,6 ≤ conf < 0,85 | Ghi log, trạng thái **Chờ xác nhận** |
| ≥ 0,85 | Ghi log và **tự động xác nhận** |

Đổi ngưỡng ở `LOG_CONF_THRESHOLD` và `AUTO_SUBMIT_THRESHOLD` trong `utils/config.py`.

### 4.3. Luồng xử lý

```text
Tải ảnh lên khung (camera_id, slot)
        │
GET /camera/frame?session=exam|study
        │
DetectionPipeline.submit()  → hàng đợi ảnh
        │   gom tối đa 4 ảnh cách nhau ≤ ~80 ms
MỘT luồng suy luận: model.predict(batch)     (GPU + FP16 nếu có CUDA, ngược lại CPU)
        │
Lọc theo loại phòng (SESSION_LABELS) → vẽ bbox + nhãn tiếng Việt → trả ảnh cho khung
        │
Mỗi detection ≥ 0,6: một ảnh bằng chứng (1 bbox) → hàng đợi bằng chứng (tối đa 256)
        │
MỘT luồng ghi log: lưu ảnh vào data_model/evidence/ + INSERT Violation_Logs (FIFO) → live_events.notify()
        │
Panel nhật ký hỏi /violations/live?since=… mỗi giây → cập nhật thẻ thay đổi
```

Điểm cần biết:

- Mỗi ảnh chỉ dự đoán và ghi log một lần cho mỗi loại phòng. Đổi giữa Phòng thi và Phòng thường thì dự đoán lại, nhưng **không ghi lại** nhãn đã có log (theo dõi bằng `logged_labels`). Muốn ghi lại toàn bộ thì tải lại ảnh.
- Backend nạp và chạy thử model ngay khi khởi động (`warmup_async`) nên ảnh đầu tiên không phải chờ.
- Khung hiển thị có tất cả bounding box; ảnh bằng chứng trong log chỉ có đúng một box.
- Nhãn trên box dựng bằng Pillow với font có tiếng Việt (`src/services/vi_draw.py`). Tìm font theo thứ tự: biến `EDUWATCH_FONT` → thư mục `view/asset/fonts/` → font hệ thống (Segoe UI/Arial/Tahoma, DejaVu...) → font của matplotlib. Font thiếu chữ tiếng Việt bị bỏ qua; không có font phù hợp (hoặc `EDUWATCH_BBOX_ASCII=1`) thì nhãn hiện **không dấu**.

## 5. Kiến trúc và cấu trúc thư mục

```text
Trình duyệt ── Streamlit (frontend_app.py, cổng 8501) ── HTTP ── FastAPI (backend_app.py, cổng 8000) ── SQLite
                  │                                                  │
                  └── iframe: camera, nhật ký, bảng, tòa nhà ────────┘ (HTML/JS trong view/asset, gọi thẳng API)
```

```text
AI_model/                 Trọng số YOLO (yolo_eduwatch.pt)
data_model/               eduwatch.db, avatar/, evidence/ (ảnh bằng chứng)
logs/                     Nhật ký thay đổi (CHANGELOG.md) và bản lưu ghi chú cũ
src/
  backend/                Router FastAPI: login, signup, admin, buildings, building_viewers,
                          camera, violation, request
  database_query/         Truy vấn SQL: admin, auth, buildings_manager, notifications, profile, violation_logs
  frontend/               Gọi API từ Streamlit: camera_request, login_request, signup_request, profile_service
  services/               camera_services, detection_pipeline, vi_draw, save_violation_services,
                          violation_log_services, live_events, avatar_services, profile_service, load_report_record
utils/                    config.py (cấu hình, ngưỡng, nhãn), db.py (kết nối SQLite), helper.py, labels_vi.py
view/
  navigation.py           Khai báo trang theo role
  pages/                  Trang Streamlit (admin/, supervision/, security_guard/, auth/, logs.py, profile.py)
  component/              Thành phần dùng chung (topbar, thông báo, bảng, biểu đồ, bộ lọc camera...)
  asset/                  HTML/JS cho iframe (camera, violation_panel, admin_table, buildings...)
  style/                  CSS (global, auth, camera, detector, profile, table, violation, buildings)
backend_app.py            Ứng dụng FastAPI (CORS, lifespan: bật WAL, nạp trước model)
frontend_app.py           Ứng dụng Streamlit (đăng nhập, điều hướng, topbar, sidebar)
init_db.py                Tạo schema và dữ liệu khởi tạo
run_app.py                Chạy cả backend và giao diện bằng một lệnh
run_windows.bat           Trình khởi động cho Windows
```

## 6. Cài đặt và chạy

Yêu cầu: Python 3.10 trở lên, file `AI_model/yolo_eduwatch.pt` và `data_model/eduwatch.db`.

### Windows (khuyến nghị)

Bấm đúp `run_windows.bat`. Script tự tạo `.venv`, cài thư viện lần đầu, chạy backend và giao diện rồi mở
trình duyệt tại `http://localhost:8501`. Hoặc trong môi trường ảo: `python run_app.py` (Ctrl+C dừng cả hai).

### Thủ công (mọi hệ điều hành)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Terminal 1: backend
uvicorn backend_app:app --host 127.0.0.1 --port 8000

# Terminal 2: giao diện
streamlit run frontend_app.py
```

Chưa có database thì chạy `python init_db.py` để tạo schema và dữ liệu khởi tạo.

### Lưu ý

- **GPU NVIDIA**: cài PyTorch bản CUDA trước (xem https://pytorch.org/get-started/locally/); model tự dùng GPU + FP16. Không có GPU thì tự chạy CPU.
- Không dùng `--reload` khi chạy thật: mỗi lần lưu file backend sẽ nạp lại model.
- Đặt project ở đường dẫn ngắn (ví dụ `C:\EduWatch`). Không nén kèm `.venv`/`venv` khi gửi project.
- Tài khoản khởi tạo từ `init_db.py`: `AD001` (admin), `GV123` (giảng viên), `BV001` (bảo vệ). Mật khẩu mặc định xem trong `init_db.py`; **đổi ngay khi dùng thật**.

## 7. Cấu hình

| Biến môi trường | Mặc định | Ý nghĩa |
|---|---|---|
| `EDUWATCH_API_HOST` | `127.0.0.1` | Địa chỉ backend. Dùng `127.0.0.1` thay vì `localhost` để tránh trễ IPv6 trên Windows |
| `EDUWATCH_API_PORT` | `8000` | Cổng backend |
| `EDUWATCH_UI_PORT` | `8501` | Cổng giao diện (dùng trong `run_app.py`) |
| `EDUWATCH_FONT` | (trống) | Đường dẫn font `.ttf` có tiếng Việt cho nhãn trên bounding box |
| `EDUWATCH_BBOX_ASCII` | (trống) | `1` để ép nhãn bounding box hiện tiếng Việt không dấu |

Tham số trong code:

| Tham số | Vị trí | Giá trị |
|---|---|---|
| Ngưỡng ghi log / tự xác nhận | `utils/config.py` | 0,6 / 0,85 |
| Nhãn theo loại phòng | `utils/config.py` (`SESSION_LABELS`) | study: 3 nhãn, exam: 8 nhãn |
| Kích thước suy luận, NMS IoU, số box tối đa | `src/services/camera_services.py` | 320, 0,85, 1000 |
| Batch tối đa, cửa sổ gom batch | `src/services/detection_pipeline.py` | 4 ảnh, 0,08 giây |
| Ảnh lưu tối đa, dung lượng tải lên, cạnh dài tối đa | `src/services/camera_services.py` | 64, 10 MB, 1280 px |
| Hàng đợi bằng chứng | `src/services/detection_pipeline.py` | 256 |

## 8. Cơ sở dữ liệu và dữ liệu mẫu

SQLite `data_model/eduwatch.db`, bật chế độ WAL. Mọi truy vấn đi qua `utils/db.py` (luôn đóng kết nối, timeout 30 giây).

| Bảng | Nội dung |
|---|---|
| `Users` | Tài khoản, vai trò (`0` admin, `1` giảng viên, `2` bảo vệ, `-1` chờ phân quyền), trạng thái khóa |
| `Buildings`, `Rooms`, `Cameras` | Tòa nhà → phòng → camera (4 góc/phòng); có cờ ngừng hoạt động |
| `Violation_Logs` | Vi phạm: camera, nhãn tiếng Anh, thời gian, `session` (`exam`/`study`), ảnh, confidence, `review_status` (`pending`/`confirmed`/`wrong`) |
| `System_Requests` | Biên bản (`bien_ban`) và báo cáo sự cố (`su_co`) kèm trạng thái duyệt |
| `Notifications` | Thông báo gửi tới người dùng khi có yêu cầu mới / được duyệt / bị hủy |

**Dữ liệu mẫu trong bản đang kèm theo** (7 tòa nhà, 21 phòng, 84 camera, 1269 log, 36 yêu cầu): phần lớn log là dữ liệu minh họa
(nhãn tiếng Việt như "Ngủ gật", "Cúi người sâu"), dùng ảnh `data_model/evidence/illustrative_*.jpg` (8 ảnh có watermark **ẢNH MINH HỌA**
và một bounding box). Nhiều log cùng loại dùng chung một ảnh minh họa. Các ảnh này **chỉ để kiểm tra giao diện, không phải bằng chứng thật**.
Log do model ghi có nhãn tiếng Anh và ảnh `detection_*.jpg`. Muốn số liệu thống kê chỉ phản ánh model, hãy xóa các log mẫu trước khi đánh giá.

Script `restore_illustrative_evidence.py` (gán ảnh minh họa cho bản ghi thiếu ảnh) không còn nằm trong bản project hiện tại.

## 9. API chính

Backend chạy tại `http://127.0.0.1:8000`.

| Nhóm | Endpoint |
|---|---|
| Tài khoản | `POST /login`, `POST /signup` |
| Quản trị người dùng | `GET /admin/users`, `PUT /admin/users/{id}/role`, `PUT /admin/users/{id}/status`, `PUT /admin/users/{id}/password` |
| Tòa nhà | `GET /locations`, `POST/PUT /locations/buildings`, `/locations/rooms`, `/locations/cameras`, `GET /locations/panel`, `GET /locations/panel_viewer` |
| Camera | `POST /camera/upload?camera_id=&slot=` (body là bytes ảnh), `GET /camera/frame?camera_id=&slot=&session=`, `GET /camera/status`, `POST /model/start`, `POST /model/stop` |
| Vi phạm | `GET /violations`, `GET /violations/live?session=&since=`, `GET /violations/panel?session=`, `POST /violations/{id}/review` |
| Biên bản / sự cố | `POST /requests/{id}/approve`, `POST /requests/{id}/reject` |
| Ảnh bằng chứng | `GET /evidence/{tên_file}` (file tĩnh) |

`GET /camera/status` trả thêm `pipeline` (ảnh/log đang chờ, số batch, số log đã ghi/bỏ qua) để theo dõi hàng đợi.

## 10. Sử dụng camera (tải ảnh lên)

1. Vào **Giám sát trực tiếp**, chọn tòa nhà và phòng đang hoạt động.
2. Với giảng viên: chọn **Phòng thi** hoặc **Phòng thường** ở bộ chọn chế độ, rồi bật AI.
3. Nhấp vào một khung (hoặc kéo thả) để tải ảnh JPG/PNG/WEBP/BMP, tối đa 10 MB. Nhấp lại để thay ảnh. Nút phóng to ở góc khung dùng để xem toàn màn hình.
4. Khung thứ *i* gắn với camera thứ *i* của phòng (thiếu thì dùng camera đầu tiên), nên vi phạm được ghi đúng phòng.
5. Log mới xuất hiện ở panel bên phải ngay khi có; dùng nút **Xác nhận** hoặc **Báo sai** để duyệt.

Nên dùng ảnh chụp từ **góc đầu phòng hoặc cuối phòng** để có kết quả đáng tin nhất (xem mục 2.1).

## 11. Hướng phát triển

Ưu tiên theo mức tác động tới độ chính xác:

1. Bổ sung dữ liệu và gán nhãn cho các góc camera còn yếu (cửa chính, cửa phụ), huấn luyện lại và đánh giá riêng từng góc.
2. Thêm bảng đánh giá định lượng theo lớp, theo góc và theo loại phòng; thử `IMGSZ` lớn hơn.
3. Cho phép bật/tắt AI theo từng góc camera (cột `Cameras.vi_tri_goc` đã có) để chỉ chạy tự động ở góc đã kiểm chứng.
4. Áp dụng điều kiện thời gian của bảng sự kiện (ví dụ ngủ gật kéo dài > 15 giây) bằng cách xét chuỗi ảnh/video.
5. Xác thực và phân quyền ở phía FastAPI; băm mật khẩu bằng Argon2/PBKDF2.
6. Nhận luồng video/RTSP thật thay cho tải ảnh lên; lưu ảnh tải lên bền vững.
7. Thêm kiểm thử tự động và cập nhật thời gian thực cho trang Nhật ký vi phạm và Thống kê.
