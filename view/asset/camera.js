__TOGGLE_CAMERA__

let recording = false;
let detectorActive = true;

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

function showAllCameras() {
  const grid = document.getElementById("grid");
  grid.classList.remove("expanded");
  document.querySelectorAll(".camera-box").forEach(box => {
    box.classList.remove("selected", "hidden");
  });
}

async function toggleRecording() {
  const button = document.getElementById("recordButton");
  const next = !recording;
  const ok = await post(next ? "http://localhost:8000/start" : "http://localhost:8000/stop");
  if (!ok) return;
  recording = next;
  button.classList.toggle("active", recording);
  document.getElementById("recordText").textContent = recording ? "Dừng ghi" : "Ghi hình";
}

async function toggleDetector() {
  const next = !detectorActive;
  const ok = await post(next ? "http://localhost:8000/model/start" : "http://localhost:8000/model/stop");
  if (!ok) return;
  detectorActive = next;
  const button = document.getElementById("detectorSwitch");
  button.classList.toggle("on", detectorActive);
  button.classList.toggle("off", !detectorActive);
  document.getElementById("detectorState").textContent = detectorActive ? "Đang hoạt động" : "Đã tắt";
}

function takeSnapshot() {
  const camera = document.querySelector(".camera-box.selected img") || document.querySelector(".camera-box img");
  if (!camera) return;
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
