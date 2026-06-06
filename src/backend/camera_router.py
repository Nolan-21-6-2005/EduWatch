import time
import cv2
import streamlit as st
from fastapi import APIRouter
from utils.model_path import getmodel_path
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
from utils.camera_config import (
    latest_detections,
    last_detect_time,
    is_running,
    is_active,
    COOLDOWN,
    placeholder_frame,
)

router = APIRouter()

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
def gen_frames(latest_detections, last_detect_time):
    try:
        while True:
            success, frame = cap.read()
            
            if not success:
                yield display(placeholder_frame)
                time.sleep(0.1)
                continue

            if not is_running:
                yield display(placeholder_frame)
                time.sleep(0.1)
                continue

            if is_active:
                results = model(frame, imgsz=320)

                for box in results[0].boxes:
                    conf = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    label = model.names[cls_id]

                    if conf > 0.8:
                        current_time = time.time()
                        last_time = last_detect_time.get(label, 0)

                        if current_time - last_time > COOLDOWN:
                            latest_detections.append({
                                "label": label,
                                "confidence": conf
                            })

                            last_detect_time[label] = current_time

                output_frame = results[0].plot()

            else:
                output_frame = frame
            yield display(output_frame)

    except Exception as e:
        print("ERROR:", e)

#=== Backend FastAPI ===
@router.get("/video")
def video_feed():
    return StreamingResponse(
        gen_frames(latest_detections, last_detect_time),
        media_type='multipart/x-mixed-replace; boundary=frame')

@router.get("/detections")       
def detections():
    data = list(latest_detections)
    return data

@router.post("/start")
def start_camera():
    global is_running
    is_running = True
    return {"status": "started"}

@router.post("/stop")
def stop_camera():
    global is_running
    is_running = False
    return {"status": "stopped"}

@router.post("/model/start")
def activate():
    global is_active
    is_active = True
    return {"predict": "started"}

@router.post("/model/stop")
def deactivate():
    global is_active
    is_active = False
    return {"predict": "stopped"}

