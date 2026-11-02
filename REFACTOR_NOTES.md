# Refactor điều hướng Streamlit

## Điều gì đã thay đổi?

- Bỏ `st.session_state["page"]`.
- Dùng `st.navigation()` làm router cho toàn bộ app.
- Dashboard được chia thành các `st.Page()` theo từng role.
- Bỏ `streamlit-option-menu` khỏi luồng Dashboard.
- Bỏ các file trung gian:
  - `view/dashboards/admin.py`
  - `view/dashboards/supervision.py`
  - `view/dashboards/security_guard.py`
  - `view/component/sidebar/admin.py`
  - `view/component/sidebar/supervision.py`
  - `view/component/sidebar/security_guard.py`
- `view/navigation.py` là nơi duy nhất khai báo các trang Dashboard.
- `view/pages/...` giữ phần giao diện/chức năng của từng trang.
- Sidebar hiện là sidebar mặc định của Streamlit, chứa navigation và thông tin tài khoản.
- Đăng nhập/đăng ký vẫn là hai page riêng; trạng thái đăng nhập chỉ dùng `professor_id` và `role`.

## Chạy project

```bash
streamlit run frontend_app.py
```

Backend vẫn chạy theo cách cũ của project.

## Cấu trúc điều hướng mới

```text
frontend_app.py
    |
    +-- chưa đăng nhập
    |      +-- Đăng nhập
    |      +-- Đăng ký
    |
    +-- đã đăng nhập
           |
           +-- role 0: Quản trị
           |      +-- Thống kê báo cáo
           |      +-- Giám sát trực tiếp
           |      +-- Nhật ký vi phạm
           |      +-- Danh sách tòa nhà
           |      +-- Quản lý người dùng
           |
           +-- role 1: Giám sát
           |      +-- Giám sát trực tiếp
           |      +-- Nhật ký vi phạm
           |      +-- Xuất biên bản
           |
           +-- role 2: An ninh
                  +-- Giám sát an ninh
                  +-- Trạng thái thiết bị
                  +-- Báo cáo sự cố
```

Lưu ý: project dùng `st.navigation()` nên không dùng cơ chế tự động quét thư mục `pages/` của Streamlit. Đây là chủ ý để có thể thay đổi danh sách page theo `role`.


## Violation log / HTML-CSS refactor (2026-09-28)

- `view/pages/logs.py` no longer contains hard-coded violation rows.
- Violation log data is read from `Violation_Logs` and joined with `Cameras`, `Rooms`, `Buildings`.
- The monitoring violation panel and the full violation-log page use the same DB source and review API.
- Removed the four seeded/sample violation rows from `init_db.py` and from the bundled SQLite database.
- `camera_router.py` now persists qualifying YOLO detections into `Violation_Logs` and stores evidence images under `data_model/evidence/`.
- Long iframe HTML was moved into:
  - `view/asset/admin_table.html`
  - `view/asset/camera.html`
  - `view/asset/violation_panel.html`
- Long JavaScript was moved into matching asset files.
- CSS is separated under `view/style/` into global/auth/camera/security/admin/layout/topbar/detector/responsive styles, plus dedicated `table.css`, `camera.css`, and `violation.css`.
- The violation table uses the same Medcare-style table component as user/building management, with real evidence thumbnails, confidence, status, search, pagination, CSV export, and review actions.


## Cleanup / stabilization (2026-11-01)

- Tách HTML camera control bar thành `view/component/control_bar.py` và ghép vào iframe qua `camera_request.py`.
- Truyền role tường minh cho trang camera; role bảo vệ không hiển thị control bar.
- Bộ chọn tòa nhà/phòng của các trang camera lấy dữ liệu từ SQLite, loại các tòa nhà/phòng đã ngừng hoạt động.
- Bỏ ảnh stock khỏi các ô camera chưa có nguồn video; hiển thị trạng thái chưa kết nối.
- Đổi nút thao tác `/start` và `/stop` thành bật/tắt luồng camera, không gọi nhầm là ghi hình vì project chưa có chức năng lưu video.
- Sửa lưu bằng chứng vi phạm, API review, banner số vi phạm chờ xác nhận, bộ lọc ngày báo cáo và khóa biểu đồ trùng nhau.
- Gỡ các bản HTML/JS trùng, router/component/trang cũ không còn được sử dụng và bytecode `__pycache__`.
- Thêm `.gitignore`, `requirements.txt` và cập nhật hướng dẫn chạy.
- Thêm API quản lý người dùng mà bảng `admin_table.js` đã gọi nhưng backend trước đó chưa đăng ký; loại bỏ nút xóa tài khoản trùng chức năng khóa.
- Tài khoản đăng ký mới được backend ép về role chờ phân quyền và trạng thái khóa; API đăng nhập chỉ chấp nhận tài khoản đang hoạt động.
- Sửa `init_db.py`: tên tòa nhà khớp database, bổ sung `Rooms.monitor_mode`, unique index cho phòng/camera và seed có thể chạy lặp mà không nhân bản dữ liệu.
- Đồng bộ font Be Vietnam Pro và màu nền giữa các trang; sửa CSS selector của segmented control theo đúng widget key.

## Update 2026-11-01 — shared report/building views and camera roles

- Added `view/component/report_list.py` for shared date/status/category/search filtering and request-table rendering.
- Updated teacher field-report and guard incident-report pages to use the shared list component while keeping their submission dialogs separate.
- Fixed request table mapping so incident reports use incident type, building, room, and description instead of exam-report fields.
- Unified the building viewer/admin panel around `buildings.html` + `buildings.js`; viewer mode suppresses edit/add/status actions.
- Changed camera control bar to supervision-only snapshot/stream controls. Admin and security camera pages are read-only.
- Moved AI activation to the supervision filter row and widened the latest-violation column.
- Added CSS for the actual violation-card class names emitted by `violation_panel.js`, producing compact thumbnail/content cards.
