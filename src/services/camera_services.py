"""Dịch vụ camera dựa trên ảnh tải lên (không còn dùng webcam).

Mỗi khung camera (slot 1-4) của một camera trong DB giữ tối đa một ảnh mới nhất
trong bộ nhớ. Khi AI đang bật, ảnh được chuyển cho DetectionPipeline (detection_pipeline.py):
cả 4 khung được dự đoán cùng lúc bằng một model, ảnh có khung nhận diện được trả về và các
vi phạm đủ độ tin cậy được ghi vào Violation_Logs lần lượt theo hàng đợi.
"""
from __future__ import annotations

import os
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
CONF_THRESHOLD = camera_state.LOG_CONF_THRESHOLD  # >= 0.6 mới vẽ/ghi log; >= 0.85 tự submit
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
    annotated: dict = field(default_factory=dict)  # session -> JPEG có khung nhận diện
    pending: dict = field(default_factory=dict)    # session -> yêu cầu AI đang chờ
    logged_labels: set = field(default_factory=set)  # nhãn đã ghi log, tránh ghi trùng khi đổi phòng
    lock: threading.Lock = field(default_factory=threading.Lock)


_store: dict[str, UploadedImage] = {}
_store_lock = threading.Lock()


@lru_cache(maxsize=1)
def _device_args() -> dict:
    """GPU NVIDIA (CUDA) thì chạy GPU + FP16; không có thì chạy CPU. Nhận ra tự động."""
    try:
        import torch

        if torch.cuda.is_available():
            return {"device": 0, "half": True}
        # CPU: dùng hết nhân vật lý hợp lý, tránh tranh chấp luồng với server/Streamlit.
        torch.set_num_threads(max(1, min(os.cpu_count() or 4, 8)))
    except Exception:
        pass
    return {"device": "cpu"}


@lru_cache(maxsize=1)
def get_model():
    from ultralytics import YOLO  # nạp muộn để backend khởi động nhanh

    return YOLO(str(getmodel_path()))  # str(): ultralytics/torch xử lý đường dẫn Windows ổn định


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
    session_labels=camera_state.SESSION_LABELS,
    predict_kwargs=_device_args,
)


def warmup_async() -> None:
    """Nạp model và chạy thử một ảnh trống ở nền khi backend khởi động, để ảnh đầu tiên
    không phải chờ nạp model (lần đầu có thể mất vài chục giây trên Windows)."""

    def _run():
        try:
            pipeline.submit(np.zeros((IMGSZ, IMGSZ, 3), np.uint8), 0, 0, "study").result(
                timeout=INFERENCE_TIMEOUT * 2
            )
            print("Model AI đã sẵn sàng.")
        except Exception as error:
            print("Không thể khởi động trước model:", error)

    threading.Thread(target=_run, name="ew-warmup", daemon=True).start()


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
        if session in image.annotated:  # mỗi loại phòng dự đoán một lần
            return image.annotated[session]
        if session not in image.pending:
            image.pending[session] = pipeline.submit(
                image.frame, camera_id, slot, session,
                skip_labels=frozenset(image.logged_labels), logged=image.logged_labels,
            )
        future = image.pending[session]

    try:
        annotated = future.result(timeout=INFERENCE_TIMEOUT)  # ndarray đã vẽ bounding box
    except FutureTimeout:
        return image.jpeg  # AI chưa xong: tạm hiện ảnh gốc, lần tải sau sẽ chờ tiếp
    except Exception as error:
        print("Lỗi nhận diện ảnh:", error)
        with image.lock:
            if image.pending.get(session) is future:
                image.pending.pop(session, None)  # cho phép thử lại ở lần tải sau
        return image.jpeg

    with image.lock:
        if session not in image.annotated:
            image.annotated[session] = _encode(annotated)  # mã hóa JPEG chạy song song giữa các khung
        return image.annotated[session]
