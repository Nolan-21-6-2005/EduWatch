// Bố cục lưới camera: 2x2 <-> một camera lớn + ba thumbnail.
const shell = document.getElementById("shell");
const grid = document.getElementById("grid");

function allBoxes() {
    return Array.from(grid.querySelectorAll(".camera-box"));
}

function selectCamera(box) {
    if (box.classList.contains("selected")) return;
    shell.classList.add("focus");
    grid.classList.add("focus");
    allBoxes().forEach(item => {
        item.classList.toggle("selected", item === box);
        item.classList.toggle("thumb", item !== box);
    });
    syncFocusHeader(box);
}

function showAllCameras() {
    if (document.fullscreenElement) document.exitFullscreen();
    shell.classList.remove("focus");
    grid.classList.remove("focus");
    allBoxes().forEach(item => item.classList.remove("selected", "thumb"));
}

// Nút trên mỗi khung: camera đang chọn -> toàn màn hình, camera khác -> phóng to.
function onExpand(event, button) {
    event.stopPropagation();
    const box = button.closest(".camera-box");
    if (!box.classList.contains("selected")) {
        selectCamera(box);
        return;
    }
    if (document.fullscreenElement) {
        document.exitFullscreen();
    } else if (box.requestFullscreen) {
        box.requestFullscreen().catch(() => {});
    }
}

function syncFocusHeader(box) {
    document.getElementById("focusTitle").textContent = box.dataset.name;
    const chip = document.getElementById("focusStatus");
    const source = box.querySelector(".cam-top .cam-status");
    chip.dataset.state = box.dataset.state;
    chip.textContent = source ? source.textContent : "";
}
