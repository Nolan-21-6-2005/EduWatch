import time
import sqlite3
from datetime import datetime
from pathlib import Path
import cv2
import streamlit as st
from fastapi import APIRouter
from utils.model_path import getmodel_path
from utils.database_path import getdatabase_path
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
import utils.camera_config as camera_state

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = BASE_DIR / "data_model" / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def _save_violation(
    label: str, 
    confidence: float, 
    frame, 
    camera_id: int | None, 
    session: str
):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    image_path = EVIDENCE_DIR / f"detection_{timestamp}.jpg"
    if not cv2.imwrite(str(image_path), frame):
        image_path = None

    with sqlite3.connect(getdatabase_path()) as conn:
        cursor = conn.execute(
            """
            INSERT INTO Violation_Logs
            (camera_id, loai_vi_pham, thoi_gian, session, image_path, confidence, is_confirmed, review_status)
            VALUES (?, ?, ?, ?, ?, ?, 0, 'pending')
            """,
            (
                camera_id,
                label,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                session,
                str(image_path.relative_to(BASE_DIR)) if image_path else None,
                confidence,
            ),
        )
        conn.commit()
        return cursor.lastrowid


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

#=== Backend FastAPI ===
@router.get("/video")
def video_feed(
        camera_id: int | None = None, 
        session: str = "study"
    ):
    return StreamingResponse(
        gen_frames(
            camera_state.latest_detections, 
            camera_state.last_detect_time, 
            camera_id, 
            session
        ),
        media_type='multipart/x-mixed-replace; boundary=frame')

@router.get("/detections")       
def detections():
    data = list(camera_state.latest_detections)
    return data

@router.post("/start")
def start_camera():
    camera_state.is_running = True
    return {"status": "started"}

@router.post("/stop")
def stop_camera():
    camera_state.is_running = False
    return {"status": "stopped"}

@router.post("/model/start")
def activate():
    camera_state.is_active = True
    return {"predict": "started"}

@router.post("/model/stop")
def deactivate():
    camera_state.is_active = False
    return {"predict": "stopped"}

