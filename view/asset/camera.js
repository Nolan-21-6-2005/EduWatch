__TOGGLE_CAMERA__

const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;
let detectorActive = null; // chưa biết cho tới lần hỏi trạng thái đầu tiên

// ---------- Trạng thái từng khung: đang tải -> đã có ảnh / chưa có ảnh / lỗi ----------
// Khóa trạng thái giữ nguyên (live/idle/unconfigured/error) để dùng lại CSS hiện có.
const STATE_TEXT = {
  connecting: "Đang tải...",
  live: "Đã có ảnh",
  idle: "Đã có ảnh",
  unconfigured: "Chưa có ảnh",
  error: "Lỗi",
};
const NOTE_TEXT = {
  connecting: "Đang tải ảnh",
  unconfigured: "Nhấp để tải ảnh lên",
  error: "Không tải được ảnh",
};

function setCameraState(box, state, note) {
  box.dataset.state = state;
  box.querySelectorAll(".cam-status").forEach(chip => {
    chip.dataset.state = state;
    chip.textContent = STATE_TEXT[state];
  });
  const noteEl = box.querySelector(".cam-note");
  if (noteEl) noteEl.textContent = note || NOTE_TEXT[state] || box.dataset.idleText || "";
  const stats = box.querySelector(".cam-stats");
  if (stats) {
    const has = box.dataset.hasImage === "1";
    stats.innerHTML = `Kích thước: ${has ? box.dataset.size : "—"}<br>Nguồn: ${has ? "Ảnh tải lên" : "—"}`;
  }
  if (box.classList.contains("selected")) syncFocusHeader(box);
}

function showPlaceholder(box) {
  const img = box.querySelector("img");
  if (box.dataset.blobUrl) URL.revokeObjectURL(box.dataset.blobUrl);
  box.dataset.blobUrl = "";
  box.dataset.hasImage = "";
  img.src = img.dataset.placeholder;
  setCameraState(box, "unconfigured");
}

// Lấy ảnh hiện tại của khung từ backend (ảnh gốc, hoặc có khung nhận diện khi AI bật).
async function loadFrame(box) {
  const token = String(Date.now() + Math.random());
  box.dataset.loadToken = token;
  if (box.dataset.hasImage !== "1") setCameraState(box, "connecting");
  try {
    const response = await fetch(`${box.dataset.frameUrl}&v=${Date.now()}`);
    if (box.dataset.loadToken !== token) return; // đã có yêu cầu mới hơn
    if (response.status === 204) { showPlaceholder(box); return; }
    if (!response.ok) throw new Error("Không tải được ảnh");
    const url = URL.createObjectURL(await response.blob());
    const img = box.querySelector("img");
    img.onload = () => {
      box.dataset.size = `${img.naturalWidth}×${img.naturalHeight}`;
      box.dataset.hasImage = "1";
      setCameraState(box, "live");
    };
    if (box.dataset.blobUrl) URL.revokeObjectURL(box.dataset.blobUrl);
    box.dataset.blobUrl = url;
    img.src = url;
  } catch (error) {
    if (box.dataset.loadToken === token) setCameraState(box, "error", error.message);
  }
}

function flashError(box, message) {
  setCameraState(box, "error", message);
  setTimeout(() => {
    if (box.dataset.state !== "error") return;
    if (box.dataset.hasImage === "1") setCameraState(box, "live");
    else setCameraState(box, "unconfigured");
  }, 3500);
}

// ---------- Tải ảnh lên ----------
async function uploadImage(box, file) {
  if (!file) return;
  if (!file.type.startsWith("image/")) { flashError(box, "Chỉ nhận tệp ảnh"); return; }
  if (file.size > MAX_UPLOAD_BYTES) { flashError(box, "Ảnh quá lớn (tối đa 10 MB)"); return; }
  setCameraState(box, "connecting", "Đang tải ảnh lên");
  try {
    const response = await fetch(box.dataset.uploadUrl, {
      method: "POST",
      headers: {"Content-Type": file.type},
      body: file,
    });
    if (!response.ok) {
      let detail = "Tải ảnh lên thất bại";
      try { detail = (await response.json()).detail || detail; } catch (_) {}
      throw new Error(detail);
    }
    await loadFrame(box);
  } catch (error) {
    flashError(box, error.message === "Failed to fetch" ? "Không kết nối được máy chủ" : error.message);
  }
}

// Nhấp vào khung = chọn ảnh (nút phóng to vẫn dùng để phóng to / toàn màn hình).
function pickImage(box, event) {
  if (document.fullscreenElement) return;
  box.querySelector(".cam-file").click();
}

function bindUploads() {
  document.querySelectorAll(".camera-box").forEach(box => {
    const input = box.querySelector(".cam-file");
    box.querySelector("img").dataset.placeholder = box.querySelector("img").src;
    input.addEventListener("click", event => event.stopPropagation());
    input.addEventListener("change", () => {
      uploadImage(box, input.files[0]);
      input.value = ""; // cho phép chọn lại cùng một tệp
    });
    box.addEventListener("dragover", event => {
      event.preventDefault();
      box.style.outline = "3px dashed #4ca66b";
    });
    ["dragleave", "drop"].forEach(name => box.addEventListener(name, () => { box.style.outline = ""; }));
    box.addEventListener("drop", event => {
      event.preventDefault();
      uploadImage(box, event.dataTransfer.files[0]);
    });
  });
}

// ---------- Theo dõi bật/tắt AI: tải lại ảnh để có/không có khung nhận diện ----------
async function refreshDetectorStatus() {
  try {
    const response = await fetch("http://localhost:8000/camera/status");
    if (!response.ok) return;
    const active = Boolean((await response.json()).detector_active);
    if (detectorActive !== null && active !== detectorActive) {
      document.querySelectorAll(".camera-box").forEach(box => {
        if (box.dataset.hasImage === "1") loadFrame(box);
      });
    }
    detectorActive = active;
  } catch (error) { /* backend tạm thời không phản hồi: bỏ qua */ }
}

function takeSnapshot() {
  const box = document.querySelector(".camera-box.selected") || document.querySelector(".camera-box");
  const img = box && box.querySelector("img");
  if (!img || box.dataset.hasImage !== "1") {
    alert("Khung này chưa có ảnh.");
    return;
  }
  const link = document.createElement("a");
  link.download = "eduwatch-snapshot.jpg";
  link.href = box.dataset.blobUrl;
  link.click();
}

bindUploads();
document.querySelectorAll(".camera-box").forEach(loadFrame);
refreshDetectorStatus();
setInterval(refreshDetectorStatus, 2000);
