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
