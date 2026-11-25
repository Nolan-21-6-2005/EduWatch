"""Pipeline nhận diện vi phạm đa luồng, dùng MỘT model cho cả 4 khung camera.

    luồng yêu cầu (tối đa 4 khung cùng lúc)
        │  submit(frame) -> Future
        ▼
    [hàng đợi ảnh] ──► LUỒNG SUY LUẬN (duy nhất, giữ model)
                         gom tối đa 4 ảnh thành 1 batch  ──►  1 lần predict cho 4 khung
                         vẽ tất cả bounding box để hiển thị camera
                         │                       │
                         │ ảnh đã vẽ (Future)    │ mỗi detection -> ảnh bằng chứng riêng,
                         │                       │ chỉ có một bounding box
                         ▼                       ▼
                   luồng yêu cầu mã hóa   [hàng đợi bằng chứng] ──► LUỒNG GHI LOG
                   JPEG để hiển thị                                 (lần lượt, đúng thứ tự vào hàng đợi)

Vì sao chỉ một luồng chạm vào model: một đối tượng YOLO dùng chung không an toàn khi nhiều
luồng gọi predict cùng lúc (trạng thái predictor bị ghi đè). Thay vì chạy 4 lần song song
trên model, ta đưa 4 ảnh vào CÙNG MỘT lần predict (batch): vẫn là "dự đoán 4 khung cùng một
lúc" nhưng không có tranh chấp, và thường nhanh hơn chạy lần lượt từng ảnh.

Ghi log chỉ do một luồng đảm nhiệm nên từng detection đủ ngưỡng được lưu thành một hàng
riêng trong Violation_Logs. Mỗi hàng có một ảnh bằng chứng chỉ chứa bounding box tương ứng.
"""
from __future__ import annotations

import queue
import threading
import time

import cv2

from src.services.vi_draw import draw_detection, label_color
from utils.labels_vi import vi_label
from concurrent.futures import Future
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class _Job:
    frame: Any
    camera_id: int
    slot: int
    session: str
    future: Future
    skip_labels: frozenset = frozenset()  # nhãn đã ghi log cho ảnh này (không ghi lại)


@dataclass
class _Evidence:
    label: str
    confidence: float
    frame: Any
    camera_id: int
    slot: int
    session: str


class DetectionPipeline:
    def __init__(
        self,
        model_loader: Callable[[], Any],
        save_fn: Callable[..., Any],
        *,
        max_batch: int = 4,
        batch_window: float = 0.08,
        imgsz: int = 320,
        threshold: float = 0.8,
        nms_iou: float = 0.85,
        max_det: int = 1000,
        log_queue_size: int = 256,
        on_detect: Callable[[dict], None] | None = None,
        label_map: dict[str, str] | None = None,
        session_labels: dict[str, frozenset[str]] | None = None,
        predict_kwargs: Callable[[], dict] | None = None,
    ):
        """
        model_loader: trả về model (gọi một lần, trong luồng suy luận).
        save_fn: save_fn(label, confidence, frame, camera_id, session) ghi một vi phạm.
        max_batch / batch_window: gom tối đa ``max_batch`` ảnh, chờ thêm tối đa ``batch_window``
            giây sau ảnh đầu tiên để các khung gửi gần nhau cùng vào một batch.
        threshold: chỉ vẽ và ghi vi phạm có độ tin cậy lớn hơn hoặc bằng ngưỡng này (0.6).
        session_labels: nhãn được nhận diện theo session; detection ngoài tập này bị bỏ.
        nms_iou: ngưỡng IoU cho NMS. Tăng ngưỡng để hạn chế loại nhầm các box
            cùng nhãn ở gần/đè lên nhau; vẫn có thể loại box trùng lặp của cùng một đối tượng.
        max_det: số detection tối đa YOLO trả về trên mỗi ảnh.
        label_map: nhãn model -> nhãn vi phạm. Chỉ các lớp có trong bảng được nhận diện; ảnh vẽ và
            bằng chứng dùng nhãn mới. Model không có lớp nào trong bảng thì giữ nguyên nhãn gốc.
        """
        self._model_loader = model_loader
        self._save_fn = save_fn
        self._max_batch = max_batch
        self._batch_window = batch_window
        self._imgsz = imgsz
        self._threshold = threshold
        self._nms_iou = float(nms_iou)
        self._max_det = int(max_det)
        self._on_detect = on_detect
        self._label_map = label_map or {}
        # session -> tập nhãn được phép (phòng thi / phòng thường). Thiếu session = không lọc.
        self._session_labels = session_labels or {}
        self._predict_kwargs = predict_kwargs or (lambda: {})  # device/half tùy máy
        self._class_ids: list[int] | None = None  # lớp được nhận diện (None = tất cả)
        self._display_names: dict[int, str] = {}  # id lớp -> nhãn hiển thị

        self._jobs: queue.Queue[_Job] = queue.Queue()
        self._evidence: queue.Queue[_Evidence] = queue.Queue(maxsize=log_queue_size)
        self._model = None
        self._start_lock = threading.Lock()
        self._started = False

        self._stats_lock = threading.Lock()
        self._batches = 0
        self._images = 0
        self._last_batch_size = 0
        self._logged = 0
        self._dropped = 0

    # ---------- API ----------
    def submit(self, frame, camera_id: int, slot: int, session: str,
               skip_labels=frozenset(), logged: set | None = None) -> Future:
        """Đưa một ảnh vào hàng đợi; Future trả về kết quả predict của ảnh đó."""
        self._ensure_started()
        job = _Job(frame, int(camera_id), int(slot), session, Future(), frozenset(skip_labels))
        job.logged = logged  # tập nhãn đã ghi của ảnh; pipeline bổ sung khi ghi log
        self._jobs.put(job)
        return job.future

    def stats(self) -> dict:
        with self._stats_lock:
            return {
                "inference_pending": self._jobs.qsize(),
                "log_pending": self._evidence.qsize(),
                "batches": self._batches,
                "images": self._images,
                "last_batch_size": self._last_batch_size,
                "logged": self._logged,
                "dropped": self._dropped,
            }

    def wait_logs(self, timeout: float | None = None) -> bool:
        """Chờ đến khi hàng đợi bằng chứng được ghi hết (dùng khi kiểm thử/tắt máy chủ)."""
        deadline = None if timeout is None else time.monotonic() + timeout
        while self._evidence.unfinished_tasks:
            if deadline is not None and time.monotonic() > deadline:
                return False
            time.sleep(0.01)
        return True

    # ---------- luồng ----------
    def _ensure_started(self) -> None:
        if self._started:
            return
        with self._start_lock:
            if self._started:
                return
            threading.Thread(target=self._inference_loop, name="ew-inference", daemon=True).start()
            threading.Thread(target=self._log_loop, name="ew-log-writer", daemon=True).start()
            self._started = True

    def _inference_loop(self) -> None:
        while True:
            batch = [self._jobs.get()]
            deadline = time.monotonic() + self._batch_window
            while len(batch) < self._max_batch:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                try:
                    batch.append(self._jobs.get(timeout=remaining))
                except queue.Empty:
                    break
            self._run_batch(batch)

    def _run_batch(self, batch: list[_Job]) -> None:
        try:
            if self._model is None:
                self._setup_model(self._model_loader())
            kwargs = {"classes": self._class_ids} if self._class_ids else {}
            results = self._model(
                [job.frame for job in batch],
                imgsz=self._imgsz,
                verbose=False,
                conf=self._threshold,
                iou=self._nms_iou,
                max_det=self._max_det,
                agnostic_nms=False,
                **self._predict_kwargs(),
                **kwargs,
            )
        except Exception as error:  # lỗi model: báo cho mọi yêu cầu trong batch
            for job in batch:
                job.future.set_exception(error)
            return

        with self._stats_lock:
            self._batches += 1
            self._images += len(batch)
            self._last_batch_size = len(batch)

        for job, result in zip(batch, results):
            try:
                original = result.orig_img
                result = self._filter_by_session(result, job.session)
                if result is None:  # không có nhãn hợp lệ: trả ảnh gốc, không ghi log
                    annotated = original.copy()
                else:
                    annotated = self._annotate(result)
                    self._enqueue_evidence(job, result, annotated)  # theo thứ tự ảnh trong batch
            except Exception as error:
                job.future.set_exception(error)
                continue
            job.future.set_result(annotated)  # ảnh đã vẽ khung (ndarray)

    def _setup_model(self, model) -> None:
        """Chọn các lớp vi phạm của model và nhãn hiển thị tương ứng."""
        names = dict(model.names)
        wanted = [i for i, n in names.items() if n in self._label_map]
        if wanted:
            self._class_ids = wanted
            self._display_names = {i: self._label_map[names[i]] for i in wanted}
        else:  # model không có lớp nào trong bảng: giữ nguyên nhãn gốc
            self._class_ids = None
            self._display_names = names
        self._model = model

    def _filter_by_session(self, result, session: str):
        """Chỉ giữ detection có nhãn thuộc loại phòng (exam/study) của ảnh."""
        allowed = self._session_labels.get(session)
        boxes = getattr(result, "boxes", None)
        if allowed is None or boxes is None or len(boxes) == 0:
            return result
        keep = [
            i for i, box in enumerate(boxes)
            if self._display_names.get(int(box.cls[0]), "") in allowed
        ]
        if len(keep) == len(boxes):
            return result
        if not keep:
            return None  # không còn detection hợp lệ cho loại phòng này
        return result[keep]

    def _annotate(self, result):
        """Ảnh có bounding box + nhãn (không hiện độ chính xác)."""
        if result is None:
            return None
        # Tự vẽ (không dùng result.plot): cv2/ultralytics không hiển thị được chữ có dấu tiếng Việt.
        frame = result.orig_img.copy()
        height, width = frame.shape[:2]
        for box in getattr(result, "boxes", None) or []:
            label = self._display_names.get(int(box.cls[0]), str(int(box.cls[0])))
            x1, y1, x2, y2 = [int(round(v)) for v in box.xyxy[0].tolist()]
            draw_detection(
                frame,
                (max(0, x1), max(0, y1), min(width - 1, x2), min(height - 1, y2)),
                vi_label(label),
                label_color(label),
            )
        return frame

    def _enqueue_evidence(self, job: _Job, result, annotated) -> None:
        """Đưa từng detection đủ ngưỡng vào hàng đợi với ảnh chỉ có một bbox.

        Ảnh ``annotated`` vẫn được dùng để hiển thị trên khung camera (tất cả bbox).
        Ảnh bằng chứng được tạo riêng từ ảnh gốc cho từng detection, vì vậy hai
        đối tượng cùng nhãn vẫn tạo thành hai bản ghi và hai ảnh độc lập.
        """
        boxes = getattr(result, "boxes", None)
        original = getattr(result, "orig_img", None)
        if boxes is None or original is None:
            return

        height, width = original.shape[:2]
        # Không dùng dict/set theo label ở đây: mỗi phần tử trong result.boxes
        # là một detection riêng, kể cả khi nhiều box có cùng class/label.
        for detection_index, box in enumerate(boxes, start=1):
            confidence = float(box.conf[0])
            if confidence < self._threshold:
                continue

            class_id = int(box.cls[0])
            label = self._display_names.get(class_id, str(class_id))
            if label in job.skip_labels:  # đã ghi log nhãn này cho ảnh (đổi loại phòng)
                continue
            x1, y1, x2, y2 = [int(round(value)) for value in box.xyxy[0].tolist()]
            x1 = max(0, min(x1, width - 1))
            y1 = max(0, min(y1, height - 1))
            x2 = max(0, min(x2, width - 1))
            y2 = max(0, min(y2, height - 1))
            if x2 <= x1 or y2 <= y1:
                continue

            # Mỗi bằng chứng là một bản sao ảnh gốc với đúng MỘT bbox.
            evidence_frame = original.copy()
            # Nhãn trên ảnh là tiếng Việt; DB vẫn lưu nhãn tiếng Anh chuẩn.
            # Ẩn confidence trên ảnh bằng chứng; confidence vẫn được lưu trong DB
            # để thống kê/đánh giá và không ảnh hưởng ngưỡng lọc detection.
            draw_detection(evidence_frame, (x1, y1, x2, y2), vi_label(label), label_color(label))

            evidence = _Evidence(
                label, confidence, evidence_frame,
                job.camera_id, job.slot, job.session,
            )
            if getattr(job, "logged", None) is not None:
                job.logged.add(label)
            # Chờ writer giải phóng hàng đợi nếu đang đầy thay vì bỏ mất detection.
            self._evidence.put(evidence)

            if self._on_detect:
                self._on_detect({
                    "label": label,
                    "confidence": confidence,
                    "camera_id": job.camera_id,
                    "slot": job.slot,
                    "detection_index": detection_index,
                })

    def _log_loop(self) -> None:
        while True:
            evidence = self._evidence.get()
            try:
                self._save_fn(
                    evidence.label, evidence.confidence, evidence.frame,
                    evidence.camera_id, evidence.session,
                )
                with self._stats_lock:
                    self._logged += 1
            except Exception as error:  # một bằng chứng lỗi không được làm dừng hàng đợi
                print("Không thể lưu violation log:", error)
            finally:
                self._evidence.task_done()
