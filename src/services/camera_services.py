import cv2
import time
from functools import lru_cache
from ultralytics import YOLO
import utils.config as camera_state
from utils.helper import getmodel_path
from src.services.save_violation_services import _save_violation

# === Ham lay model ===
@lru_cache(maxsize=1)
def get_model():
    return YOLO(getmodel_path())

# === Ham ket noi camera ===
@lru_cache(maxsize=1)
def get_camera():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Không tìm thấy camera")
        camera_state.camera_connected = False
        cap.release()
        return None

    camera_state.camera_connected = True
    return cap

# === Ham hien thi khung hinh ===
def display(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    frame_bytes = buffer.tobytes()

    return (
        b'--frame\r\n'
        b'Content-Type: image/jpeg\r\n\r\n' +
        frame_bytes +
        b'\r\n'
    )

cap = get_camera()
model = get_model()

# === Ham nhan dien doi tuong === 
def gen_frames(
    latest_detections, 
    last_detect_time, 
    camera_id: int = None, 
    session: str = "study"
):
    try:
        while True:
            if cap is None or not cap.isOpened():
                yield display(camera_state.placeholder_frame)
                time.sleep(0.5)
                continue

            success, frame = cap.read()
            
            if not success:
                yield display(camera_state.placeholder_frame)
                time.sleep(0.1)
                continue

            if not camera_state.is_running:
                yield display(camera_state.placeholder_frame)
                time.sleep(0.1)
                continue

            if camera_state.is_active:
                results = model(frame, imgsz=320)

                for box in results[0].boxes:
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]

                    if conf > 0.8:
                        current_time = time.time()
                        last_time = last_detect_time.get(label, 0)

                        if current_time - last_time > camera_state.COOLDOWN:
                            latest_detections.append({
                                "label": label,
                                "confidence": conf,
                            })
                            try:
                                _save_violation(label, conf, frame, camera_id, session)
                            except Exception as error:
                                print("Không thể lưu violation log:", error)

                            last_detect_time[label] = current_time

                output_frame = results[0].plot()

            else:
                output_frame = frame
            yield display(output_frame)

    except Exception as e:
        camera_state.camera_connected = False
        print("ERROR:", e)
