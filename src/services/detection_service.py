import cv2
import time
from src.ai_core.camera_manager import CameraManager
from src.ai_core.detector_model import Detector
from src.utils.model_config import AI_PATH

# Khởi tạo các thực thể toàn cục
camera_manager = CameraManager(0)  # Thay bằng số 1, 2 hoặc đường dẫn RTSP nếu là Cam IP
detector = Detector(AI_PATH)

def display(frame):
    if frame is None:
        return b''
    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
    return (
        b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' +
        buffer.tobytes() +
        b'\r\n'
    )

def gen_frames():
    while True:
        success, frame = camera_manager.read_frame()
        
        if not success or frame is None:
            # Nếu chưa có hình, gửi một ảnh đen tạm thời để giữ luồng stream không bị ngắt kết nối
            time.sleep(0.1)
            continue

        try:
            # Kiểm tra trạng thái AI trực tiếp từ thực thể điều khiển
            if detector.is_active():
                results = detector.detect_object(frame)
                if results and len(results) > 0:
                    output_frame = results[0].plot()
                    yield display(output_frame)
                else:
                    yield display(frame)
            else:
                yield display(frame)
        except Exception as e:
            print(f"Lỗi xử lý khung hình: {e}")
            yield display(frame)
            
        time.sleep(0.03)  # Giới hạn luồng Web ở khoảng ~30 FPS để tối ưu băng thông
