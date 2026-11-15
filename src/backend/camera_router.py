from fastapi import APIRouter, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response

import utils.config as camera_state
from src.database_query.buildings_manager import camera_exists
from src.services import camera_services

router = APIRouter()

SESSIONS = {"exam", "study"}


def _check_target(camera_id: int, slot: int) -> None:
    if not 1 <= slot <= camera_services.MAX_SLOTS:
        raise HTTPException(status_code=400, detail="Khung camera không hợp lệ")
    if not camera_exists(camera_id):
        raise HTTPException(status_code=404, detail="Không tìm thấy camera")


# === Ảnh tải lên cho từng khung camera ===
@router.post("/camera/upload")
async def upload_image(request: Request, camera_id: int, slot: int):
    """Nhận ảnh dạng bytes thô (Content-Type: image/*) cho khung `slot` của camera."""
    _check_target(camera_id, slot)
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > camera_services.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Ảnh quá lớn (tối đa 10 MB).")
    data = await request.body()
    try:
        return await run_in_threadpool(camera_services.save_upload, camera_id, slot, data)
    except camera_services.ImageError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.get("/camera/frame")
def camera_frame(camera_id: int, slot: int, session: str = "study"):
    """Ảnh hiện tại của khung; có khung nhận diện nếu AI đang bật."""
    _check_target(camera_id, slot)
    if session not in SESSIONS:
        session = "study"
    jpeg = camera_services.get_frame(camera_id, slot, session)
    if jpeg is None:
        return Response(status_code=204)  # khung chưa có ảnh: không phải lỗi
    return Response(content=jpeg, media_type="image/jpeg", headers={"Cache-Control": "no-store"})


@router.get("/camera/status")
def camera_status():
    return {
        "detector_active": bool(camera_state.is_active),
        "pipeline": camera_services.pipeline_stats(),
    }


@router.get("/detections")
def detections():
    return list(camera_state.latest_detections)


@router.post("/model/start")
def activate():
    camera_state.is_active = True
    return {"predict": "started"}


@router.post("/model/stop")
def deactivate():
    camera_state.is_active = False
    return {"predict": "stopped"}
