import cv2
import time
import sqlite3
import streamlit as st
from ultralytics import YOLO
import utils.config as camera_state
from utils.helper import getmodel_path
from src.services.save_violation_services import _save_violation

# === Ham lay model ===
@st.cache_resource
def get_model():
    return YOLO(getmodel_path())

# === Ham ket noi camera ===
@st.cache_resource
def get_camera():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Không tìm thấy camera")
        return None
    
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
                            except sqlite3.Error as error:
                                print("Không thể lưu violation log:", error)

                            last_detect_time[label] = current_time

                output_frame = results[0].plot()

            else:
                output_frame = frame
            yield display(output_frame)

    except Exception as e:
        print("ERROR:", e)
