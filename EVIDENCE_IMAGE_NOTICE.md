# Lưu ý về ảnh minh họa trong nhật ký vi phạm

Tám ảnh `data_model/evidence/illustrative_*.jpg` được tạo làm dữ liệu minh họa cho giao diện. Mỗi ảnh có một bounding box và tên loại vi phạm tương ứng; trên ảnh có watermark **ẢNH MINH HỌA** và bounding box màu bao quanh hành vi được minh họa.

Các bản ghi cũ bị thiếu `image_path` được gắn ảnh mẫu theo `loai_vi_pham`. Nhiều bản ghi cùng loại sẽ dùng chung một ảnh minh họa. Những ảnh này chỉ phục vụ demo/kiểm tra giao diện, không phải ảnh được camera ghi nhận và không được dùng làm bằng chứng xử lý vi phạm thực tế.

Để chạy lại thao tác trên database hiện tại, từ thư mục gốc project chạy:

```bash
python restore_illustrative_evidence.py
```

Script chỉ cập nhật các bản ghi thiếu ảnh hoặc có đường dẫn ảnh không còn tồn tại; các đường dẫn ảnh hợp lệ được giữ nguyên.


Riêng nhãn “Cúi người sâu”: ảnh minh họa đã được thay bằng tình huống người hạ thấp thân và rúc xuống dưới gầm bàn; bounding box màu đỏ khoanh vùng người thực hiện hành vi. Tư thế được thể hiện là người vẫn ngồi trên ghế, gập thân và đầu xuống dưới mặt bàn. Ảnh chỉ minh họa tư thế/hành vi cần xem xét, không khẳng định người đó đang gian lận.
