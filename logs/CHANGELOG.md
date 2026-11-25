# Nhật ký thay đổi (Changelog)

Ghi lại các thay đổi đáng kể của EduWatch, mới nhất ở trên cùng. Định dạng mỗi mục:
**Thêm** (tính năng mới), **Thay đổi** (hành vi khác trước), **Sửa** (lỗi), **Gỡ bỏ**, **Kiểm tra** (cách đã xác minh).
Tài liệu sử dụng và hạn chế hiện tại nằm ở [`README.md`](../README.md). Các ghi chú gốc trước khi gom nằm ở [`archive/`](archive/).

Quy ước khi thêm mục mới: một đề mục `## [Ngày] Tên đợt thay đổi`, mỗi dòng ngắn và nêu rõ file/hàm bị ảnh hưởng.
Mục chưa rõ ngày chính xác được ghi theo tháng.

---

## [Cuối 11/2026] Model mới, nhãn theo phòng, tối ưu Windows, log thời gian thực

### Nhận diện AI
- **Thay đổi** — Model `AI_model/yolo_eduwatch.pt` được huấn luyện lại: lớp `leaning_down` được thay bằng `eating`, đủ 8 lớp theo bảng sự kiện (`sleeping`, `eating`, `leaving_seat`, `phone`, `turning_head`, `standing`, `reading`, `walking`).
- **Thêm** — Nhãn theo loại phòng (`utils/config.py`: `VIOLATION_SCOPE`, `SESSION_LABELS`). Phòng thường: `sleeping`, `eating`, `leaving_seat`. Phòng thi: cả 8 nhãn. Pipeline lọc detection theo `session` của từng ảnh (`DetectionPipeline._filter_by_session`).
- **Thay đổi** — Ngưỡng độ chính xác: từ 0,6 mới vẽ box và ghi log; từ 0,85 tự động xác nhận (trước đây ngưỡng ghi là 0,8 và tự xác nhận là 0,95). Hằng số `LOG_CONF_THRESHOLD`, `AUTO_SUBMIT_THRESHOLD`; model chạy với `conf = 0,6`.
- **Thay đổi** — Mỗi detection là một log riêng với ảnh bằng chứng một bounding box (đã đúng từ trước, được kiểm lại bằng test mô phỏng 4 detection nhiều nhãn).
- **Sửa** — Chuyển Phòng thi ↔ Phòng thường làm dự đoán lại và ghi trùng log. Nay mỗi ảnh lưu kết quả theo từng `session` và nhớ nhãn đã ghi (`logged_labels`, `skip_labels`).
- **Thêm** — Nhãn tiếng Việt: `utils/labels_vi.py` (`VIOLATION_NAMES_VI`, `vi_label()`); CSDL vẫn lưu nhãn tiếng Anh. Áp dụng cho panel log, trang Nhật ký (kể cả bộ lọc loại vi phạm), thống kê KPI, biểu đồ cột, xuất CSV. Biểu đồ gộp các tên tiếng Anh khác nhau của cùng một lỗi.
- **Thêm** — Vẽ chữ có dấu trên bounding box bằng Pillow (`src/services/vi_draw.py`); thay `result.plot()` và `cv2.putText` vốn không hiển thị được dấu. Kiểm tra font có đủ chữ tiếng Việt; nếu không có thì tự chuyển sang không dấu. Biến `EDUWATCH_FONT`, `EDUWATCH_BBOX_ASCII`.

### Nhật ký thời gian thực
- **Thêm** — `GET /violations/live?session=&since=`: panel hỏi mỗi giây, backend trả ngay nếu phiên bản chưa đổi (`src/services/live_events.py`, `notify()` sau khi ghi log và sau khi duyệt).
- **Thay đổi** — `view/asset/violation_panel.js` viết lại: chỉ thêm/sửa/xóa đúng thẻ thay đổi, hiệu ứng thẻ mới, chấm trạng thái đỏ khi mất kết nối, tạm dừng khi tab ẩn, làm mới đầy đủ mỗi 10 giây. Ảnh bằng chứng tải qua URL `/evidence/...` thay vì base64.
- **Thay đổi** — Panel và `GET /violations` lọc theo loại phòng (`?session=exam|study`).

### Tối ưu cho Windows
- **Thêm** — `run_windows.bat` và `run_app.py`: tạo `.venv`, cài thư viện, chạy backend + giao diện, mở trình duyệt; không dùng `--reload`; ép UTF-8.
- **Thêm** — `utils/db.py`: kết nối SQLite luôn đóng, timeout 30 giây, WAL, tạo chỉ mục `idx_logs_time`, `idx_logs_label`. Mọi truy vấn trong `src/database_query/` và router đã chuyển sang đây (trước đây `with sqlite3.connect()` không đóng kết nối nên Windows dễ báo "database is locked").
- **Sửa** — `cv2.imwrite` không ghi được vào đường dẫn có ký tự Unicode: nay ghi bằng `imencode` + `write_bytes`; đường dẫn ảnh lưu trong DB dùng dấu `/`.
- **Sửa** — Địa chỉ backend đổi từ `localhost` sang `127.0.0.1` (`API_BASE` trong `utils/config.py`) để tránh trễ 1–2 giây do IPv6 trên Windows.
- **Thay đổi** — Backend không còn import Streamlit (`utils/helper.py` nạp muộn `st.cache_data`).
- **Thay đổi** — Model tự chọn GPU + FP16 nếu có CUDA, ngược lại CPU; nạp và chạy thử model khi khởi động (`warmup_async`).
- **Sửa** — Lỗi in tiếng Việt ra console Windows trong luồng ghi log (`reconfigure(encoding="utf-8")`).

### Giao diện
- **Sửa** — Thanh tìm kiếm trang ở topbar không chuyển trang được với vai trò Admin và Bảo vệ. Thay `st_searchbox` (chạy trong iframe) bằng `st.selectbox` gốc; danh sách trang lấy trực tiếp từ `view/navigation.py`; chọn lại cùng một trang vẫn hoạt động. Đã bỏ `streamlit-searchbox` khỏi `requirements.txt`.

### Tài liệu
- **Thay đổi** — Viết lại `README.md` theo đúng trạng thái hiện tại, thêm mục mục tiêu đã đạt và hạn chế (đặc biệt về dữ liệu và góc camera). Gom `CHANGES_*.md`, `EVIDENCE_IMAGE_NOTICE.md`, `REFACTOR_NOTES.md` vào `logs/`.

### Kiểm tra
- Biên dịch toàn bộ file Python; kiểm tra cú pháp JavaScript.
- Test mô phỏng bằng dữ liệu giả: lọc nhãn theo phòng, log nhiều nhãn, không ghi trùng khi đổi phòng, `/violations/live`, duyệt vi phạm, dịch nhãn, bộ lọc, biểu đồ, điều hướng của 3 vai trò bằng `AppTest` của Streamlit.
- Chưa đo độ chính xác của model mới trên dữ liệu thật và chưa chạy toàn bộ ứng dụng trên Windows với camera thực.

---

## [2026-11-09] Pipeline AI đa luồng, ẩn cột Duyệt

- **Thêm** — `src/services/detection_pipeline.py`: nhiều luồng yêu cầu → hàng đợi ảnh → MỘT luồng suy luận gom tối đa 4 ảnh thành một batch → hàng đợi bằng chứng (tối đa 256) → MỘT luồng ghi log tuần tự (FIFO). Không gọi `predict` song song trên cùng một đối tượng YOLO vì không an toàn luồng. Mỗi luồng yêu cầu tự vẽ khung và mã hóa JPEG cho ảnh của nó.
- **Thay đổi** — `camera_services.get_frame()` chỉ gửi ảnh vào pipeline và chờ kết quả (timeout 60 giây; lỗi hoặc quá hạn thì hiện ảnh gốc và thử lại ở lần tải sau). Mỗi ảnh chỉ dự đoán và ghi log một lần.
- **Thay đổi** — Bằng chứng lỗi không làm dừng luồng ghi; hàng đợi đầy thì bỏ qua và đếm vào `dropped`.
- **Thay đổi** — Ẩn cột "Duyệt": `render_request_list(..., can_approve=False)` → `render_admin_table(..., can_approve=...)` → `CAN_APPROVE` trong `admin_table.js`. Chỉ hai bảng ở trang Thống kê của admin truyền `can_approve=True`. Quyền thật vẫn do `approve_request()` kiểm tra `role = 0`.

## [2026-11 — trước 11/09] Xử lý detection trùng nhãn

- **Thay đổi** — Duyệt tuần tự toàn bộ `result.boxes`, không gom theo nhãn và không chọn một detection đại diện cho mỗi nhãn. Mỗi detection đạt ngưỡng vào hàng đợi bằng chứng riêng rồi thành một dòng `Violation_Logs`.
- **Thay đổi** — NMS `iou = 0,85`, `max_det = 1000`, `agnostic_nms = False` để hạn chế loại nhầm các box cùng nhãn ở gần nhau.
- **Thay đổi** — Bounding box chỉ hiển thị tên nhãn, không in confidence; confidence vẫn lưu trong SQLite.
- **Lưu ý** — YOLO trả về box sau NMS nên không khôi phục được box đã bị loại; IoU cao có thể sinh box trùng cho cùng một đối tượng. Cần kiểm tra bằng ảnh camera thực tế.
- **Kiểm tra** — Test mô phỏng 3 detection cùng nhãn `phone` tạo 3 bằng chứng độc lập.

## [2026-11-07] Tải ảnh lên thay webcam; bộ lọc mặc định không lọc; giao diện giám sát gọn

- **Thay đổi** — Bỏ `cv2.VideoCapture(0)`, luồng MJPEG `/video`, `/start`, `/stop` và các biến webcam. Mỗi trong 4 khung camera nhận một ảnh tải lên (`POST /camera/upload`, `GET /camera/frame`); `/camera/status` chỉ còn `detector_active` (sau này thêm `pipeline`).
- **Thêm** — `get_room_camera_ids()`, `camera_exists()` trong `buildings_manager.py`; `connect_camera()` nhận `camera_ids`.
- **Thay đổi** — Bộ lọc mặc định "Tất cả"; khoảng ngày rỗng là không lọc (`date_range_bounds()`). Sửa nút "Đặt lại" ở Nhật ký vi phạm để xóa luôn giá trị các ô nhập.
- **Thay đổi** — `detector.css`: chiều cao khung camera = `100dvh - --ew-chrome-h` (min 380 px, max 880 px), bỏ `flex-basis: 820px` của Streamlit để trang vừa một màn hình. Panel nhật ký cao bằng cột camera, phần danh sách tự cuộn.
- **Thay đổi** — Thẻ vi phạm gọn: ảnh 58 px, tên + độ tin cậy cùng một dòng, hai nút Xác nhận/Báo sai cao 26 px.

## [2026-11-02] Bảng báo cáo, danh sách tòa nhà, CORS

- **Thay đổi** — Xuất biên bản và Báo cáo sự cố giữ hai trang riêng, chỉ dùng chung component bảng với 6 cột: Thời gian, Tòa nhà, Phòng học, Loại sự cố, Mô tả, Trạng thái. Bộ lọc trực tiếp dưới từng cột, phân trang 10 dòng. Dữ liệu biên bản cũ được ánh xạ vào các cột tương ứng.
- **Thay đổi** — Danh sách tòa nhà: Học viện dùng `buildings.html` + `buildings.js` (thêm/sửa/kích hoạt), Bảo vệ dùng `building_viewers.html` + `building_viewers.js` (chỉ xem); cùng bố cục ba cột.
- **Sửa** — Bộ dựng HTML thay đúng placeholder, không làm hỏng `window.__API_BASE__` và `window.__VIEWER__`.
- **Sửa** — CORS cho phép Origin `null` để preflight OPTIONS từ iframe Data URI của bảng HTML được chấp nhận.
- **Kiểm tra** — 59 file Python kiểm tra cú pháp AST, 6 file JavaScript `node --check`; preflight PUT trả 200.

## [2026-11-01] Dọn dẹp và ổn định hóa; báo cáo/tòa nhà dùng chung; phân quyền camera

- **Thêm** — `view/component/control_bar.py` (control bar tách khỏi HTML camera), `view/component/report_list.py` (lọc ngày/trạng thái/loại/tìm kiếm dùng chung), `.gitignore`, `requirements.txt`.
- **Thay đổi** — Trang camera nhận `role` tường minh; Admin và Bảo vệ chỉ xem, control bar (chụp/luồng) chỉ cho giám sát. Công tắc AI chuyển lên hàng bộ lọc của trang giám sát.
- **Thay đổi** — Bộ chọn tòa nhà/phòng lấy từ SQLite, loại tòa nhà/phòng đã ngừng hoạt động. Ô camera chưa có nguồn hiển thị trạng thái chưa kết nối thay cho ảnh stock.
- **Sửa** — Lưu bằng chứng vi phạm, API review, banner số vi phạm chờ xác nhận, bộ lọc ngày báo cáo, khóa biểu đồ trùng nhau, bảng yêu cầu của báo cáo sự cố.
- **Thêm** — API quản lý người dùng mà `admin_table.js` đã gọi nhưng backend chưa đăng ký; bỏ nút xóa tài khoản trùng chức năng khóa.
- **Thay đổi** — Tài khoản đăng ký mới bị ép về `role = -1`, `status = 0`; API đăng nhập chỉ nhận tài khoản đang hoạt động.
- **Sửa** — `init_db.py`: tên tòa nhà khớp database, thêm `Rooms.monitor_mode`, unique index phòng/camera, seed chạy lặp không nhân bản dữ liệu.
- **Gỡ bỏ** — Các bản HTML/JS trùng, router/component/trang cũ không dùng và bytecode `__pycache__`.
- **Thay đổi** — Đồng bộ font Be Vietnam Pro và màu nền; sửa CSS selector của segmented control theo đúng widget key.

## [2026-09-28] Nhật ký vi phạm lấy từ CSDL; tách HTML/CSS

- **Thay đổi** — `view/pages/logs.py` không còn dữ liệu cứng; đọc `Violation_Logs` join `Cameras`, `Rooms`, `Buildings`. Panel giám sát và trang Nhật ký dùng chung một nguồn dữ liệu và API review.
- **Gỡ bỏ** — 4 dòng vi phạm mẫu khỏi `init_db.py` và database đóng gói.
- **Thay đổi** — `camera_router.py` ghi các detection YOLO đủ điều kiện vào `Violation_Logs` và lưu ảnh bằng chứng trong `data_model/evidence/`.
- **Thay đổi** — HTML/JS dài chuyển sang `view/asset/` (`admin_table`, `camera`, `violation_panel`); CSS tách trong `view/style/` (global, auth, camera, table, violation...).
- **Thay đổi** — Bảng vi phạm dùng cùng component bảng với quản lý người dùng/tòa nhà: ảnh bằng chứng thật, confidence, trạng thái, tìm kiếm, phân trang, xuất CSV, thao tác duyệt.

## [Trước 09/2026] Điều hướng Streamlit bằng `st.navigation()`

- **Thay đổi** — Bỏ `st.session_state["page"]`; `st.navigation()` làm router duy nhất, trang chia theo `role` trong `view/navigation.py`. Trạng thái đăng nhập chỉ dùng `professor_id` và `role`. Sidebar là sidebar mặc định của Streamlit (điều hướng + thông tin tài khoản).
- **Gỡ bỏ** — `streamlit-option-menu` và các file trung gian `view/dashboards/*`, `view/component/sidebar/*`.
- **Lưu ý** — Project dùng `st.navigation()` nên không dùng cơ chế quét thư mục `pages/` của Streamlit (để đổi danh sách trang theo `role`).

---

## Phụ lục: dữ liệu minh họa trong nhật ký vi phạm

Tám ảnh `data_model/evidence/illustrative_*.jpg` được tạo làm dữ liệu minh họa cho giao diện: mỗi ảnh có một bounding box màu, tên loại
vi phạm và watermark **ẢNH MINH HỌA**. Các bản ghi cũ thiếu `image_path` được gắn ảnh mẫu theo `loai_vi_pham`; nhiều bản ghi cùng loại dùng chung một ảnh.
Ảnh chỉ phục vụ demo/kiểm tra giao diện, **không phải ảnh camera ghi nhận và không dùng làm bằng chứng xử lý vi phạm**.
Riêng nhãn "Cúi người sâu": ảnh minh họa thể hiện người ngồi trên ghế, gập thân và đầu xuống dưới mặt bàn; chỉ minh họa tư thế cần xem xét, không khẳng định gian lận.
Script `restore_illustrative_evidence.py` (gán ảnh minh họa cho bản ghi thiếu ảnh hoặc đường dẫn không còn tồn tại) không còn trong bản project hiện tại.
