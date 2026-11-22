"""Dịch vụ camera dựa trên ảnh tải lên (không còn dùng webcam).

Mỗi khung camera (slot 1-4) của một camera trong DB giữ tối đa một ảnh mới nhất
trong bộ nhớ. Khi AI đang bật, ảnh được chuyển cho DetectionPipeline (detection_pipeline.py):
cả 4 khung được dự đoán cùng lúc bằng một model, ảnh có khung nhận diện được trả về và các
vi phạm đủ độ tin cậy được ghi vào Violation_Logs lần lượt theo hàng đợi.
"""
from __future__ import annotations

import threading
import time
from concurrent.futures import Future, TimeoutError as FutureTimeout
from dataclasses import dataclass, field
from functools import lru_cache

import cv2
import numpy as np

import utils.config as camera_state
from src.services.detection_pipeline import DetectionPipeline
from src.services.save_violation_services import _save_violation
from utils.helper import getmodel_path

MAX_SLOTS = 4
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_SIDE = 1280                      # ảnh lớn hơn sẽ được thu nhỏ khi lưu
MAX_STORED = 64                      # số ảnh tối đa giữ trong bộ nhớ
CONF_THRESHOLD = 0.8
# IoU cao hơn giúp giữ lại các box cùng nhãn có vùng chồng lấn; nếu quá cao
# có thể xuất hiện box trùng của cùng một đối tượng, cần kiểm tra bằng ảnh thực tế.
NMS_IOU_THRESHOLD = 0.85
MAX_DETECTIONS_PER_IMAGE = 1000
IMGSZ = 320
JPEG_QUALITY = 90
INFERENCE_TIMEOUT = 60.0             # giây chờ kết quả AI (lần đầu còn phải nạp model)


class ImageError(ValueError):
    """Ảnh tải lên không hợp lệ (thông báo hiển thị được cho người dùng)."""


@dataclass
class UploadedImage:
    frame: np.ndarray
    jpeg: bytes
    uploaded_at: float
    width: int
    height: int
    annotated: bytes | None = None      # ảnh có khung nhận diện (đã chạy AI)
    pending: Future | None = None       # yêu cầu AI đang chờ kết quả
    lock: threading.Lock = field(default_factory=threading.Lock)


_store: dict[str, UploadedImage] = {}
_store_lock = threading.Lock()


@lru_cache(maxsize=1)
def get_model():
    from ultralytics import YOLO  # nạp muộn để backend khởi động nhanh

    return YOLO(getmodel_path())


def _key(camera_id: int, slot: int) -> str:
    return f"{int(camera_id)}:{int(slot)}"


def _encode(frame: np.ndarray) -> bytes:
    ok, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
    if not ok:
        raise ImageError("Không thể xử lý ảnh.")
    return buffer.tobytes()


def save_upload(camera_id: int, slot: int, data: bytes) -> dict:
    """Giải mã, thu nhỏ nếu cần rồi lưu ảnh cho khung camera."""
    if not data:
        raise ImageError("Tệp ảnh trống.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise ImageError("Ảnh quá lớn (tối đa 10 MB).")
    frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise ImageError("Tệp không phải ảnh hợp lệ (hỗ trợ JPG, PNG, WEBP, BMP).")

    height, width = frame.shape[:2]
    scale = MAX_SIDE / max(height, width)
    if scale < 1:
        frame = cv2.resize(frame, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)
        height, width = frame.shape[:2]

    image = UploadedImage(
        frame=frame, jpeg=_encode(frame), uploaded_at=time.time(), width=width, height=height
    )
    with _store_lock:
        _store[_key(camera_id, slot)] = image
        while len(_store) > MAX_STORED:  # loại ảnh cũ nhất
            oldest = min(_store, key=lambda k: _store[k].uploaded_at)
            del _store[oldest]
    return {"slot": slot, "width": width, "height": height, "uploaded_at": image.uploaded_at}


def _on_detect(detection: dict) -> None:
    camera_state.latest_detections.append(
        {"label": detection["label"], "confidence": detection["confidence"]}
    )


# Một model dùng chung; 4 khung được gom vào cùng một batch, bằng chứng ghi lần lượt theo hàng đợi.
pipeline = DetectionPipeline(
    get_model,
    _save_violation,
    max_batch=MAX_SLOTS,
    imgsz=IMGSZ,
    threshold=CONF_THRESHOLD,
    nms_iou=NMS_IOU_THRESHOLD,
    max_det=MAX_DETECTIONS_PER_IMAGE,
    on_detect=_on_detect,
    label_map=camera_state.VIOLATION_LABELS,
)


def pipeline_stats() -> dict:
    return pipeline.stats()


def get_frame(camera_id: int, slot: int, session: str = "study") -> bytes | None:
    """JPEG để hiển thị: ảnh gốc, hoặc ảnh có khung nhận diện khi AI đang bật.

    Nhiều khung gọi cùng lúc (mỗi khung một luồng yêu cầu) sẽ được gom vào cùng một batch AI.
    Mỗi ảnh chỉ được dự đoán và ghi vi phạm một lần.
    """
    with _store_lock:
        image = _store.get(_key(camera_id, slot))
    if image is None:
        return None
    if not camera_state.is_active:
        return image.jpeg

    with image.lock:
        if image.annotated is not None:
            return image.annotated
        if image.pending is None:
            image.pending = pipeline.submit(image.frame, camera_id, slot, session)
        future = image.pending

    try:
        annotated = future.result(timeout=INFERENCE_TIMEOUT)  # ndarray đã vẽ bounding box
    except FutureTimeout:
        return image.jpeg  # AI chưa xong: tạm hiện ảnh gốc, lần tải sau sẽ chờ tiếp
    except Exception as error:
        print("Lỗi nhận diện ảnh:", error)
        with image.lock:
            if image.pending is future:
                image.pending = None  # cho phép thử lại ở lần tải sau
        return image.jpeg

    with image.lock:
        if image.annotated is None:
            image.annotated = _encode(annotated)  # mã hóa JPEG chạy song song giữa các khung
        return image.annotated
