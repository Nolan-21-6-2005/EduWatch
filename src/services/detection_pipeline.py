"""Pipeline nhận diện vi phạm đa luồng, dùng MỘT model cho cả 4 khung camera.

    luồng yêu cầu (tối đa 4 khung cùng lúc)
        │  submit(frame) -> Future
        ▼
    [hàng đợi ảnh] ──► LUỒNG SUY LUẬN (duy nhất, giữ model)
                         gom tối đa 4 ảnh thành 1 batch  ──►  1 lần predict cho 4 khung
                         vẽ bounding box (nhãn đã đổi tên, không hiện độ chính xác)
                         │                       │
                         │ ảnh đã vẽ (Future)    │ bằng chứng = ảnh đã vẽ khung
                         ▼                       ▼
                   luồng yêu cầu mã hóa   [hàng đợi bằng chứng] ──► LUỒNG GHI LOG
                   JPEG để hiển thị                                 (lần lượt, đúng thứ tự vào hàng đợi)

Vì sao chỉ một luồng chạm vào model: một đối tượng YOLO dùng chung không an toàn khi nhiều
luồng gọi predict cùng lúc (trạng thái predictor bị ghi đè). Thay vì chạy 4 lần song song
trên model, ta đưa 4 ảnh vào CÙNG MỘT lần predict (batch): vẫn là "dự đoán 4 khung cùng một
lúc" nhưng không có tranh chấp, và thường nhanh hơn chạy lần lượt từng ảnh.

Ghi log chỉ do một luồng đảm nhiệm nên bằng chứng được lưu vào Violation_Logs lần lượt theo
hàng đợi (FIFO), không tranh chấp ghi SQLite và không trùng tên tệp ảnh.
"""
from __future__ import annotations

import queue
import threading
import time
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
        log_queue_size: int = 256,
        on_detect: Callable[[dict], None] | None = None,
        label_map: dict[str, str] | None = None,
    ):
        """
        model_loader: trả về model (gọi một lần, trong luồng suy luận).
        save_fn: save_fn(label, confidence, frame, camera_id, session) ghi một vi phạm.
        max_batch / batch_window: gom tối đa ``max_batch`` ảnh, chờ thêm tối đa ``batch_window``
            giây sau ảnh đầu tiên để các khung gửi gần nhau cùng vào một batch.
        threshold: chỉ ghi vi phạm có độ tin cậy lớn hơn ngưỡng này.
        label_map: nhãn model -> nhãn vi phạm. Chỉ các lớp có trong bảng được nhận diện; ảnh vẽ và
            bằng chứng dùng nhãn mới. Model không có lớp nào trong bảng thì giữ nguyên nhãn gốc.
        """
        self._model_loader = model_loader
        self._save_fn = save_fn
        self._max_batch = max_batch
        self._batch_window = batch_window
        self._imgsz = imgsz
        self._threshold = threshold
        self._on_detect = on_detect
        self._label_map = label_map or {}
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
    def submit(self, frame, camera_id: int, slot: int, session: str) -> Future:
        """Đưa một ảnh vào hàng đợi; Future trả về kết quả predict của ảnh đó."""
        self._ensure_started()
        job = _Job(frame, int(camera_id), int(slot), session, Future())
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
            results = self._model([job.frame for job in batch], imgsz=self._imgsz,
                                  verbose=False, **kwargs)
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

    def _annotate(self, result):
        """Ảnh có bounding box + nhãn (không hiện độ chính xác)."""
        result.names = self._display_names
        return result.plot(conf=False)

    def _enqueue_evidence(self, job: _Job, result, annotated) -> None:
        best: dict[str, float] = {}  # mỗi loại vi phạm chỉ lấy độ tin cậy cao nhất trong ảnh
        for box in result.boxes:
            confidence = float(box.conf[0])
            label = self._display_names[int(box.cls[0])]
            if confidence > self._threshold and confidence > best.get(label, 0.0):
                best[label] = confidence
        for label, confidence in best.items():
            # Bằng chứng là ảnh đã vẽ bounding box, không phải ảnh gốc.
            evidence = _Evidence(label, confidence, annotated, job.camera_id, job.slot, job.session)
            try:
                self._evidence.put(evidence, timeout=1)
            except queue.Full:
                with self._stats_lock:
                    self._dropped += 1
                print(f"Hàng đợi bằng chứng đầy, bỏ qua: {label} (camera {job.camera_id})")
                continue
            if self._on_detect:
                self._on_detect({"label": label, "confidence": confidence,
                                 "camera_id": job.camera_id, "slot": job.slot})

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
