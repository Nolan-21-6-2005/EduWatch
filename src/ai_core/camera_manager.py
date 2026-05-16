import cv2
import threading
import time

class CameraManager:
    def __init__(self, source):
        self.cap = cv2.VideoCapture(source)
        # Thiết lập độ phân giải vừa phải để AI xử lý mượt hơn
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.ret = False
        self.frame = None
        self.is_running = True
        
        if not self.cap.isOpened():
            print(f"❌ Không thể mở camera source: {source}")
            return

        # Khởi chạy luồng đọc camera độc lập
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        print("✅ Luồng đọc phần cứng Camera đã kích hoạt.")

    def _update_loop(self):
        while self.is_running:
            if self.cap.isOpened():
                self.ret, self.frame = self.cap.read()
            time.sleep(0.01)  # Tránh quá tải CPU

    def read_frame(self):
        # Trả về khung hình mới nhất ngay lập tức mà không phải chờ phần cứng phản hồi
        return self.ret, self.frame

    def disconnect(self):
        self.is_running = False
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
