> **Bản lưu:** ghi chú gốc, giữ nguyên để đối chiếu và có thể đã lỗi thời. Nội dung chính thức nằm ở [`../CHANGELOG.md`](../CHANGELOG.md) và [`../../README.md`](../../README.md).

# Cập nhật detection trùng nhãn

## Thay đổi
- Duyệt tuần tự toàn bộ `result.boxes`; không gom theo class/label và không chọn một detection đại diện cho mỗi nhãn.
- Mỗi detection vượt ngưỡng confidence 0.8 được đưa vào hàng đợi bằng chứng riêng, sau đó ghi một dòng riêng trong `Violation_Logs`.
- Tăng ngưỡng NMS IoU lên 0.85, đặt `max_det=1000` và giữ `agnostic_nms=False` để giảm khả năng NMS loại các bounding box cùng nhãn ở gần/chồng lấn.
- Bounding box chỉ hiển thị tên nhãn, không in confidence. Confidence vẫn được lưu trong SQLite và vẫn được dùng để lọc ngưỡng / xác định trạng thái tự xác nhận.

## Lưu ý
YOLO trả về các box sau bước Non-Maximum Suppression (NMS). Vì vậy, ứng dụng có thể lưu độc lập tất cả box YOLO trả về, nhưng không thể khôi phục các box mà NMS đã loại trước đó. IoU cao hơn giúp giữ lại nhiều box chồng lấn hơn, nhưng cũng có thể làm xuất hiện box trùng của cùng một đối tượng. Cần kiểm tra bằng ảnh camera thực tế để chọn ngưỡng phù hợp.

## Kiểm tra
- Python compileall: đạt.
- Kiểm thử mô phỏng 3 detection cùng nhãn `phone`: tạo 3 evidence độc lập.
- Kiểm tra source: `plot(conf=False)` và nhãn ảnh bằng chứng không chứa confidence.
- Chưa chạy inference trên model thật vì trọng số YOLO không nằm trong archive.
