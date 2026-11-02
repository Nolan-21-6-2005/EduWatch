# EduWatch-beta – cập nhật bảng báo cáo và danh sách tòa nhà

## 1. Xuất biên bản và Báo cáo sự cố
- Giữ nguyên hai trang, tiêu đề, nút tạo/gửi và form riêng của từng vai trò.
- Chỉ dùng chung component bảng; không gộp hai giao diện.
- Cả hai bảng có đúng thứ tự 6 cột:
  1. Thời gian
  2. Tòa nhà
  3. Phòng học
  4. Loại sự cố
  5. Mô tả
  6. Trạng thái
- Thêm bộ lọc trực tiếp dưới từng tiêu đề cột; bộ lọc kết hợp được với tìm kiếm và bộ lọc ngày/trạng thái phía trên.
- Phân trang 10 dòng mỗi trang cho cả hai bảng.
- Ánh xạ dữ liệu cũ của biên bản (môn thi/phòng thi/ghi chú) vào các cột tương ứng; nếu dữ liệu cũ không có tòa nhà riêng, thử tách từ chuỗi vị trí dạng `Tên tòa nhà - Mã phòng`.

## 2. Danh sách tòa nhà
- Trang Học viện dùng `view/asset/buildings.html` và `view/asset/buildings.js`.
- Trang Bảo vệ dùng riêng `view/asset/building_viewers.html` và `view/asset/building_viewers.js`.
- Hai trang giữ cùng bố cục ba cột; Học viện có thêm/sửa/kích hoạt-ngừng hoạt động, Bảo vệ chỉ xem.
- Sửa bộ dựng HTML để thay đúng giá trị placeholder, không làm hỏng tên biến `window.__API_BASE__` và `window.__VIEWER__`.

## 3. CORS cập nhật vai trò
- Cho phép Origin `null` trong CORS để preflight OPTIONS từ iframe Data URI của bảng HTML được chấp nhận.
- Đã kiểm tra preflight OPTIONS với PUT và Content-Type application/json: phản hồi 200 trong kiểm thử middleware.

## Kiểm tra
- 59 file Python: kiểm tra cú pháp AST, không có lỗi.
- 6 file JavaScript: `node --check`, không có lỗi.
- Chưa chạy toàn bộ ứng dụng với camera/YOLO và dữ liệu Database thực tế.
