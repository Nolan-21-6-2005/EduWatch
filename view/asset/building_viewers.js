(() => {
  const API = window.__API_BASE__ || window.location.origin;
  let data = Array.isArray(window.__LOCATIONS__) ? window.__LOCATIONS__ : [];
  let selectedBuildingId = null;
  let selectedRoomId = null;

  const els = {
    buildingList: document.getElementById("building-list"),
    roomList: document.getElementById("room-list"),
    cameraList: document.getElementById("camera-list"),
    roomHelper: document.getElementById("room-helper"),
    cameraHelper: document.getElementById("camera-helper"),
    grid: document.querySelector(".location-grid"),
    roomCard: document.querySelector('[data-kind="room"]'),
    cameraCard: document.querySelector('[data-kind="camera"]'),
  };

  const esc = v => String(v ?? "").replace(/[&<>\'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;",'"':"&quot;"}[c]));
  const statusText = active => active ? "Hoạt động" : "Ngừng hoạt động";
  const statusClass = active => active ? "active" : "inactive";

  function findBuilding(id) { return data.find(b => Number(b.id) === Number(id)); }
  function findRoom(building, id) { return building?.rooms?.find(r => Number(r.id) === Number(id)); }

  async function reloadData(preserve = true) {
    const previousBuilding = selectedBuildingId;
    const previousRoom = selectedRoomId;
    const response = await fetch(`${API}/locations`, { cache: "no-store" });
    if (!response.ok) throw new Error("Không thể đọc cơ sở dữ liệu.");
    data = await response.json();
    selectedBuildingId = preserve && findBuilding(previousBuilding) ? previousBuilding : null;
    const building = findBuilding(selectedBuildingId);
    selectedRoomId = preserve && findRoom(building, previousRoom) ? previousRoom : null;
    render();
  }

  function buildingItem(row) {
    const active = Number(row.status) === 1;
    const selected = Number(row.id) === Number(selectedBuildingId);
    return `<article class="location-item ${selected ? "active" : ""}">
      <button class="location-main" type="button" data-select="building" data-id="${row.id}" aria-pressed="${selected}">
        <div class="location-title">${esc(row.ten_toa)}</div>
        <div class="location-status">${row.room_count ?? 0} phòng · ${row.camera_count ?? 0} camera hoạt động</div>
        <span class="status-badge ${statusClass(active)}">${statusText(active)}</span>
      </button>
    </article>`;
  }

  function roomItem(row) {
    const active = Number(row.status) === 1;
    const selected = Number(row.id) === Number(selectedRoomId);
    const cameraCount = Array.isArray(row.cameras) ? row.cameras.length : 0;
    return `<article class="location-item ${selected ? "active" : ""}">
      <button class="location-main" type="button" data-select="room" data-id="${row.id}" aria-pressed="${selected}">
        <div class="location-title">${esc(row.ten_phong)}</div>
        <div class="location-status">${cameraCount} góc camera</div>
        <span class="mode-badge ${Number(row.monitor_mode) === 1 ? "exam" : "normal"}">${Number(row.monitor_mode) === 1 ? "Phòng thi" : "Phòng thường"}</span>
        <span class="status-badge ${statusClass(active)}">${statusText(active)}</span>
      </button>
    </article>`;
  }

  function cameraItem(row) {
    const active = Number(row.status) === 1;
    return `<article class="location-item">
      <div class="location-main camera-main">
        <div class="location-title">${esc(row.vi_tri_goc || `Camera #${row.id}`)}</div>
        <div class="location-source">${esc(row.video_source || "Chưa cấu hình nguồn camera")}</div>
        <span class="status-badge ${statusClass(active)}">${statusText(active)}</span>
      </div>
    </article>`;
  }

  function render() {
    const building = findBuilding(selectedBuildingId);
    const room = findRoom(building, selectedRoomId);
    els.buildingList.innerHTML = data.length ? data.map(buildingItem).join("") : `<div class="empty-hint">Chưa có tòa nhà nào trong cơ sở dữ liệu.</div>`;
    els.roomList.innerHTML = building?.rooms?.length ? building.rooms.map(roomItem).join("") : `<div class="empty-hint">${building ? "Chưa có phòng trong tòa nhà này." : "Chọn một tòa nhà để xem danh sách phòng."}</div>`;
    els.cameraList.innerHTML = room?.cameras?.length ? room.cameras.map(cameraItem).join("") : `<div class="empty-hint">${room ? "Chưa có góc camera trong phòng này." : "Chọn một phòng học để xem các góc camera."}</div>`;
    els.roomHelper.textContent = building ? building.ten_toa : "Chọn một tòa nhà";
    els.cameraHelper.textContent = room ? room.ten_phong : "Chọn một phòng học";
    els.roomCard.hidden = !building;
    els.cameraCard.hidden = !room;
    els.grid.classList.toggle("has-building", Boolean(building));
    els.grid.classList.toggle("has-room", Boolean(room));
  }

  document.addEventListener("click", event => {
    const select = event.target.closest("[data-select]");
    if (!select) return;
    const kind = select.dataset.select;
    if (kind === "building") {
      selectedBuildingId = Number(select.dataset.id);
      selectedRoomId = null;
    } else if (kind === "room") {
      selectedRoomId = Number(select.dataset.id);
    }
    render();
  });

  reloadData(false).catch(error => {
    els.buildingList.innerHTML = `<div class="empty-hint">${esc(error.message || "Không thể đọc dữ liệu từ eduwatch.db.")}</div>`;
    render();
  });
})();
