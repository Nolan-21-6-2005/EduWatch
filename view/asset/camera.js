__TOGGLE_CAMERA__

let cameraRunning = true;
let detectorActive = false;

async function post(url) {
  try {
    const response = await fetch(url, {method:"POST"});
    if (!response.ok) throw new Error("Request failed");
    return true;
  } catch (error) {
    console.error(error);
    return false;
  }
}

// ---------- Trạng thái từng camera: kết nối -> trực tiếp / nghỉ / mất kết nối ----------
const STATE_TEXT = {
  connecting: "Kết nối...",
  live: "Trực tiếp",
  idle: "Tạm dừng",
  unconfigured: "Chưa cấu hình",
  error: "Mất kết nối",
};
const NOTE_TEXT = {
  connecting: "Đang kết nối luồng camera",
  idle: "Luồng camera đang tạm dừng",
  unconfigured: "Nguồn video chưa được cấu hình",
  error: "Mất kết nối luồng camera",
};

function setCameraState(box, state) {
  box.dataset.state = state;
  box.querySelectorAll(".cam-status").forEach(chip => {
    chip.dataset.state = state;
    chip.textContent = STATE_TEXT[state];
  });
  const note = box.querySelector(".cam-note");
  if (note) note.textContent = NOTE_TEXT[state] || box.dataset.idleText || "";
  // Chỉ hiển thị thông số khi có luồng thật; chưa có thì để "—".
  const live = state === "live";
  const stats = box.querySelector(".cam-stats");
  if (stats) {
    stats.innerHTML = `FPS: ${live ? box.dataset.fps : "—"}<br>Độ trễ: ${live ? box.dataset.latency : "—"} ms`;
  }
  if (box.classList.contains("selected")) syncFocusHeader(box);
}

function initCameras() {
  document.querySelectorAll(".camera-box").forEach(box => {
    const img = box.querySelector("img");
    const initialState = box.dataset.state || "connecting";
    if (initialState === "unconfigured") {
      setCameraState(box, "unconfigured");
      return;
    }
    const onLoad = () => setCameraState(box, "live");
    const onError = () => setCameraState(box, "error");
    setCameraState(box, "connecting");
    img.addEventListener("load", onLoad);
    img.addEventListener("error", onError);
    if (img.complete) (img.naturalWidth ? onLoad : onError)();
  });
  refreshCameraStatus();
}

async function refreshCameraStatus() {
  try {
    const response = await fetch("http://localhost:8000/camera/status");
    if (!response.ok) throw new Error("Không lấy được trạng thái camera");
    const status = await response.json();
    const mainCamera = document.querySelector(".camera-box");
    if (mainCamera) {
      const state = !status.connected ? "error" : status.running ? "live" : "idle";
      setCameraState(mainCamera, state);
    }
    cameraRunning = Boolean(status.running);
    const button = document.getElementById("cameraStreamButton");
    const label = document.getElementById("cameraStreamText");
    if (button && label) {
      button.classList.toggle("running", cameraRunning);
      label.textContent = cameraRunning ? "Tạm dừng" : "Tiếp tục";
    }
    detectorActive = Boolean(status.detector_active);
    const detectorButton = document.getElementById("detectorSwitch");
    const detectorLabel = document.getElementById("detectorState");
    if (detectorButton && detectorLabel) {
      detectorButton.classList.toggle("on", detectorActive);
      detectorButton.classList.toggle("off", !detectorActive);
      detectorLabel.textContent = detectorActive ? "Đang hoạt động" : "Ngừng hoạt động";
    }
  } catch (error) {
    const mainCamera = document.querySelector(".camera-box");
    if (mainCamera) setCameraState(mainCamera, "error");
  }
}

async function toggleCameraStream() {
  const button = document.getElementById("cameraStreamButton");
  const label = document.getElementById("cameraStreamText");
  if (!button || !label) return;

  const next = !cameraRunning;
  button.disabled = true;
  const ok = await post(next ? "http://localhost:8000/start" : "http://localhost:8000/stop");
  button.disabled = false;
  if (!ok) return;

  cameraRunning = next;
  button.classList.toggle("running", cameraRunning);
  label.textContent = cameraRunning ? "Tạm dừng" : "Tiếp tục";
  await refreshCameraStatus();
}

async function toggleDetector() {
  const mainCamera = document.querySelector(".camera-box");
  if (!detectorActive && mainCamera?.dataset.state !== "live") {
    alert("Cần kết nối camera trước khi bật AI.");
    return;
  }
  const next = !detectorActive;
  const ok = await post(next ? "http://localhost:8000/model/start" : "http://localhost:8000/model/stop");
  if (!ok) return;
  detectorActive = next;
  const button = document.getElementById("detectorSwitch");
  button.classList.toggle("on", detectorActive);
  button.classList.toggle("off", !detectorActive);
  document.getElementById("detectorState").textContent = detectorActive ? "Đang hoạt động" : "Ngừng hoạt động";
}

function takeSnapshot() {
  const camera = document.querySelector(".camera-box.selected img") || document.querySelector(".camera-box img");
  if (!camera) return;
  if (camera.closest(".camera-box")?.dataset.state !== "live") {
    alert("Không thể chụp ảnh khi camera chưa có luồng trực tiếp.");
    return;
  }
  const canvas = document.createElement("canvas");
  canvas.width = camera.naturalWidth || camera.clientWidth;
  canvas.height = camera.naturalHeight || camera.clientHeight;
  const ctx = canvas.getContext("2d");
  try {
    ctx.drawImage(camera, 0, 0, canvas.width, canvas.height);
    const link = document.createElement("a");
    link.download = "eduwatch-snapshot.jpg";
    link.href = canvas.toDataURL("image/jpeg", .92);
    link.click();
  } catch (error) {
    alert("Không thể chụp ảnh từ camera này.");
  }
}

initCameras();
setInterval(refreshCameraStatus, 5000);
