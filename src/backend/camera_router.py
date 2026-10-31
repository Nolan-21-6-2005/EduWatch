from fastapi import APIRouter
import utils.config as camera_state
from fastapi.responses import StreamingResponse
from src.services.camera_services import gen_frames

router = APIRouter()

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

