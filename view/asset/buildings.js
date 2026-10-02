(() => {
  const API = window.__API_BASE__ || window.location.origin;
  let data = Array.isArray(window.__LOCATIONS__) ? window.__LOCATIONS__ : [];
  let selectedBuildingId = data.find(b => Number(b.status) === 1)?.id ?? data[0]?.id ?? null;
  let selectedRoomId = null;
  let modalKind = null;
  let modalId = null;

  const els = {
    buildingList: document.getElementById("building-list"),
    roomList: document.getElementById("room-list"),
    cameraList: document.getElementById("camera-list"),
    roomHelper: document.getElementById("room-helper"),
    cameraHelper: document.getElementById("camera-helper"),
    addRoom: document.getElementById("add-room"),
    addCamera: document.getElementById("add-camera"),
    modal: document.getElementById("modal-backdrop"),
    modalTitle: document.getElementById("modal-title"),
    modalBody: document.getElementById("modal-body"),
    toast: document.getElementById("toast"),
  };

  const esc = v => String(v ?? "").replace(/[&<>'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;","\"":"&quot;"}[c]));
  const statusText = active => active ? "Hoạt động" : "Ngừng hoạt động";
  const statusClass = active => active ? "active" : "inactive";

  function findBuilding(id) { return data.find(b => Number(b.id) === Number(id)); }
  function findRoom(building, id) { return building?.rooms?.find(r => Number(r.id) === Number(id)); }

  function toast(msg) {
    els.toast.textContent = msg;
    els.toast.classList.add("show");
    clearTimeout(toast.timer);
    toast.timer = setTimeout(() => els.toast.classList.remove("show"), 2200);
  }

  async function request(path, options = {}) {
    const response = await fetch(`${API}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.detail || "Không thể cập nhật dữ liệu.");
    return payload;
  }

  async function reloadData(preserve = true) {
    const previousBuilding = selectedBuildingId;
    const previousRoom = selectedRoomId;
    data = await fetch(`${API}/locations`, { cache: "no-store" }).then(r => {
      if (!r.ok) throw new Error("Không thể đọc cơ sở dữ liệu.");
      return r.json();
    });
    if (preserve && findBuilding(previousBuilding)) selectedBuildingId = previousBuilding;
    else selectedBuildingId = data.find(b => Number(b.status) === 1)?.id ?? data[0]?.id ?? null;
    const building = findBuilding(selectedBuildingId);
    if (preserve && findRoom(building, previousRoom)) selectedRoomId = previousRoom;
    else selectedRoomId = building?.rooms?.find(r => Number(r.status) === 1)?.id ?? building?.rooms?.[0]?.id ?? null;
    render();
  }

  function actionButtons(kind, row) {
    const id = Number(row.id);
    const active = Number(row.status) === 1;
    const edit = `<button class="icon-btn" data-edit="${kind}" data-id="${id}" title="Chỉnh sửa">✎</button>`;
    const power = `<button class="icon-btn power" data-toggle="${kind}" data-id="${id}" title="${active ? "Ngừng hoạt động" : "Kích hoạt"}">${active ? "⏻" : "⏽"}</button>`;
    const del = `<button class="icon-btn delete" data-delete="${kind}" data-id="${id}" title="Xóa">🗑</button>`;
    return `<div class="location-actions">${edit}${power}${del}</div>`;
  }

  function buildingItem(row) {
    const active = Number(row.status) === 1;
    const selected = Number(row.id) === Number(selectedBuildingId);
    return `<article class="location-item ${selected ? "active" : ""}">
      <button class="location-main" data-select="building" data-id="${row.id}">
        <div class="location-title">${esc(row.ten_toa)}</div>
        <div class="location-status">${row.room_count ?? 0} phòng · ${row.camera_count ?? 0} camera hoạt động</div>
        <span class="status-badge ${statusClass(active)}">${statusText(active)}</span>
      </button>
      ${actionButtons("building", row)}
    </article>`;
  }

  function roomItem(row) {
    const active = Number(row.status) === 1;
    const selected = Number(row.id) === Number(selectedRoomId);
    const cameraCount = Array.isArray(row.cameras) ? row.cameras.length : 0;
    return `<article class="location-item ${selected ? "active" : ""}">
      <button class="location-main" data-select="room" data-id="${row.id}">
        <div class="location-title">${esc(row.ten_phong)}</div>
        <div class="location-status">${cameraCount} góc camera</div>
        <span class="mode-badge ${Number(row.monitor_mode) === 1 ? "exam" : "normal"}">${Number(row.monitor_mode) === 1 ? "Phòng thi" : "Phòng thường"}</span>
        <span class="status-badge ${statusClass(active)}">${statusText(active)}</span>
      </button>
      ${actionButtons("room", row)}
    </article>`;
  }

  function cameraItem(row) {
    const active = Number(row.status) === 1;
    return `<article class="location-item">
      <button class="location-main" type="button">
        <div class="location-title">${esc(row.vi_tri_goc || `Camera #${row.id}`)}</div>
        <div class="location-source">${esc(row.video_source || "Chưa cấu hình nguồn camera")}</div>
        <span class="status-badge ${statusClass(active)}">${statusText(active)}</span>
      </button>
      ${actionButtons("camera", row)}
    </article>`;
  }

  function render() {
    const building = findBuilding(selectedBuildingId);
    const room = findRoom(building, selectedRoomId);
    els.buildingList.innerHTML = data.length ? data.map(buildingItem).join("") : `<div class="empty-hint">Chưa có tòa nhà nào trong cơ sở dữ liệu.</div>`;
    els.roomList.innerHTML = building?.rooms?.length ? building.rooms.map(roomItem).join("") : `<div class="empty-hint">Vui lòng chọn một tòa nhà để xem danh sách phòng.</div>`;
    els.cameraList.innerHTML = room?.cameras?.length ? room.cameras.map(cameraItem).join("") : `<div class="empty-hint">Vui lòng chọn một phòng học để xem danh sách góc camera.</div>`;
    els.roomHelper.textContent = building ? building.ten_toa : "Chọn một tòa nhà";
    els.cameraHelper.textContent = room ? room.ten_phong : "Chọn một phòng học";
    els.addRoom.disabled = !building;
    els.addCamera.disabled = !room;
  }

  function formHtml(kind, row = {}) {
    if (kind === "building") {
      return `<form id="location-form" class="form-grid">
        <div class="form-field"><label>Tên tòa nhà</label><input name="name" required value="${esc(row.ten_toa || "")}" placeholder="Ví dụ: Giảng đường A"></div>
        <div class="form-field"><label>Trạng thái</label><select name="status"><option value="1" ${Number(row.status ?? 1) === 1 ? "selected" : ""}>Hoạt động</option><option value="0" ${Number(row.status ?? 1) === 0 ? "selected" : ""}>Ngừng hoạt động</option></select></div>
        <div class="form-actions"><button type="button" data-modal-cancel>Hủy</button><button class="primary" type="submit">Lưu</button></div>
      </form>`;
    }
    if (kind === "room") {
      const building = findBuilding(selectedBuildingId);
      return `<form id="location-form" class="form-grid">
        <div class="form-field"><label>Tòa nhà</label><select name="building_id">${data.filter(b => Number(b.status) === 1 || Number(b.id) === Number(row.building_id)).map(b => `<option value="${b.id}" ${Number(b.id) === Number(row.building_id ?? selectedBuildingId) ? "selected" : ""}>${esc(b.ten_toa)}</option>`).join("")}</select></div>
        <div class="form-field"><label>Tên phòng</label><input name="name" required value="${esc(row.ten_phong || "")}" placeholder="Ví dụ: P.101"></div>
        <div class="form-field"><label>Chế độ giám sát</label><select name="monitor_mode"><option value="0" ${Number(row.monitor_mode ?? 0) === 0 ? "selected" : ""}>Phòng thường</option><option value="1" ${Number(row.monitor_mode ?? 0) === 1 ? "selected" : ""}>Phòng thi</option></select></div>
        <div class="form-field"><label>Trạng thái</label><select name="status"><option value="1" ${Number(row.status ?? 1) === 1 ? "selected" : ""}>Hoạt động</option><option value="0" ${Number(row.status ?? 1) === 0 ? "selected" : ""}>Ngừng hoạt động</option></select></div>
        <div class="form-actions"><button type="button" data-modal-cancel>Hủy</button><button class="primary" type="submit">Lưu</button></div>
      </form>`;
    }
    return `<form id="location-form" class="form-grid">
      <div class="form-field"><label>Phòng</label><select name="room_id">${(findBuilding(selectedBuildingId)?.rooms || []).filter(r => Number(r.status) === 1 || Number(r.id) === Number(row.room_id)).map(r => `<option value="${r.id}" ${Number(r.id) === Number(row.room_id ?? selectedRoomId) ? "selected" : ""}>${esc(r.ten_phong)}</option>`).join("")}</select></div>
      <div class="form-field"><label>Vị trí góc camera</label><input name="position" required value="${esc(row.vi_tri_goc || "")}" placeholder="Góc cửa chính"></div>
      <div class="form-field"><label>Nguồn video</label><input name="video_source" value="${esc(row.video_source || "")}" placeholder="rtsp://... hoặc data/videos/..."></div>
      <div class="form-field"><label>Trạng thái</label><select name="status"><option value="1" ${Number(row.status ?? 1) === 1 ? "selected" : ""}>Hoạt động</option><option value="0" ${Number(row.status ?? 1) === 0 ? "selected" : ""}>Ngừng hoạt động</option></select></div>
      <div class="form-actions"><button type="button" data-modal-cancel>Hủy</button><button class="primary" type="submit">Lưu</button></div>
    </form>`;
  }

  function openModal(kind, row = null) {
    modalKind = kind;
    modalId = row?.id ?? null;
    els.modalTitle.textContent = `${row ? "Sửa" : "Thêm"} ${kind === "building" ? "tòa nhà" : kind === "room" ? "phòng" : "góc camera"}`;
    els.modalBody.innerHTML = formHtml(kind, row || {});
    els.modal.hidden = false;
    els.modal.querySelector("[name=name], [name=position]")?.focus();
  }

  function closeModal() { els.modal.hidden = true; modalKind = null; modalId = null; }

  async function submitForm(form) {
    const fd = new FormData(form);
    const p = Object.fromEntries(fd.entries());
    const status = Number(p.status || 0);
    let path = "", method = "POST", payload = p;
    if (modalKind === "building") {
      path = modalId ? `/locations/buildings/${modalId}` : "/locations/buildings";
      method = modalId ? "PUT" : "POST";
      payload = { name: p.name, status };
    } else if (modalKind === "room") {
      path = modalId ? `/locations/rooms/${modalId}` : "/locations/rooms";
      method = modalId ? "PUT" : "POST";
      payload = { building_id: Number(p.building_id), name: p.name, status, monitor_mode: Number(p.monitor_mode || 0) };
    } else {
      path = modalId ? `/locations/cameras/${modalId}` : "/locations/cameras";
      method = modalId ? "PUT" : "POST";
      payload = { room_id: Number(p.room_id), position: p.position, video_source: p.video_source || "", status };
    }
    const result = await request(path, { method, body: JSON.stringify(payload) });
    closeModal();
    toast(modalId ? "Đã cập nhật dữ liệu." : "Đã thêm dữ liệu.");
    await reloadData(true);
  }

  async function toggle(kind, id) {
    const find = kind === "building" ? findBuilding(id) : kind === "room" ? findRoom(findBuilding(selectedBuildingId), id) : findRoom(findBuilding(selectedBuildingId), selectedRoomId)?.cameras?.find(c => Number(c.id) === Number(id));
    const current = Number(find?.status || 0);
    const path = kind === "building" ? `/locations/buildings/${id}/status` : kind === "room" ? `/locations/rooms/${id}/status` : `/locations/cameras/${id}/status`;
    await request(path, { method: "PATCH", body: JSON.stringify({ status: current ? 0 : 1 }) });
    await reloadData(true);
    toast(current ? "Đã chuyển sang ngừng hoạt động." : "Đã kích hoạt.");
  }

  async function remove(kind, id) {
    const row = kind === "building" ? findBuilding(id) : kind === "room" ? findRoom(findBuilding(selectedBuildingId), id) : findRoom(findBuilding(selectedBuildingId), selectedRoomId)?.cameras?.find(c => Number(c.id) === Number(id));
    const label = row?.ten_toa || row?.ten_phong || row?.vi_tri_goc || `#${id}`;
    if (!window.confirm(`Bạn có chắc muốn ngừng hoạt động “${label}” không?`)) return;
    await toggle(kind, id);
  }

  document.addEventListener("click", async e => {
    const select = e.target.closest("[data-select]");
    const add = e.target.closest("[data-add]");
    const edit = e.target.closest("[data-edit]");
    const tog = e.target.closest("[data-toggle]");
    const del = e.target.closest("[data-delete]");
    try {
      if (select) {
        const kind = select.dataset.select;
        if (kind === "building") {
          selectedBuildingId = Number(select.dataset.id);
          const b = findBuilding(selectedBuildingId);
          selectedRoomId = b?.rooms?.find(r => Number(r.status) === 1)?.id ?? b?.rooms?.[0]?.id ?? null;
        } else if (kind === "room") {
          selectedRoomId = Number(select.dataset.id);
        }
        render();
        return;
      }
      if (add) {
        openModal(add.dataset.add);
        return;
      }
      if (edit) {
        const kind = edit.dataset.edit, id = Number(edit.dataset.id);
        const row = kind === "building" ? findBuilding(id) : kind === "room" ? findRoom(findBuilding(selectedBuildingId), id) : findRoom(findBuilding(selectedBuildingId), selectedRoomId)?.cameras?.find(c => Number(c.id) === id);
        openModal(kind, row);
        return;
      }
      if (tog) {
        await toggle(tog.dataset.toggle, Number(tog.dataset.id));
        return;
      }
      if (del) {
        await remove(del.dataset.delete, Number(del.dataset.id));
        return;
      }
      if (e.target.matches("[data-modal-cancel]")) closeModal();
    } catch (err) { toast(err.message || "Có lỗi xảy ra."); }
  });

  document.getElementById("modal-close").addEventListener("click", closeModal);
  els.modal.addEventListener("click", e => { if (e.target === els.modal) closeModal(); });
  els.modalBody.addEventListener("submit", async e => {
    if (!e.target.matches("#location-form")) return;
    e.preventDefault();
    try { await submitForm(e.target); } catch (err) { toast(err.message || "Không thể lưu."); }
  });

  reloadData(false).catch(err => {
    toast(err.message || "Không thể đọc dữ liệu từ eduwatch.db.");
    render();
  });
})();
