(() => {
  const TYPE = "__TABLE_TYPE__";
  const API = "__API_BASE__";
  const initial = Array.isArray(window.__EDUWATCH_DATA__) ? window.__EDUWATCH_DATA__ : [];
  const app = document.getElementById("app");
  const modal = document.getElementById("modal");
  const modalTitle = document.getElementById("modal-title");
  const modalText = document.getElementById("modal-text");
  const modalInput = document.getElementById("modal-input");
  let rows = [...initial];
  let filtered = [...rows];
  let page = 1;
  const pageSize = TYPE === "users" ? 7 : 8;
  let sortKey = "";
  let sortDir = 1;
  let pendingAction = null;

  const esc = (v) => String(v ?? "").replace(/[&<>'"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;","\"":"&quot;"}[c]));
  const icon = (name) => `<span class="material-symbols-rounded" style="font-size:17px">${name}</span>`;

  function roleName(role) {
    return ({0:"Admin",1:"Giảng viên",2:"Bảo vệ"}[role] ?? "Không xác định");
  }
  function roleClass(role) { return ({0:"admin",1:"teacher",2:"guard"}[role] ?? ""); }

  function render() {
    if (TYPE === "users") renderUsers();
    else if (TYPE === "buildings") renderBuildings();
    else renderStatistics();
  }

  function toolbar(title, placeholder="Tìm kiếm...") {
    return `<div class="toolbar">
      <div class="toolbar-left">
        <input class="search" id="search" placeholder="${placeholder}">
        ${TYPE === "statistics" ? `<input class="control" id="date-filter" type="date" value="2026-05-27" style="border-radius:10px">` : ""}
      </div>
      <div class="toolbar-right">
        <button class="control" id="sort-btn">${icon("sort")} Sắp xếp</button>
        <button class="control" id="export-btn">${icon("download")} Xuất dữ liệu</button>
      </div>
    </div>`;
  }

  function renderStatistics() {
    const totalNormal = rows.reduce((s,r)=>s+Number(r.normal||0),0);
    const totalExam = rows.reduce((s,r)=>s+Number(r.exam||0),0);
    app.innerHTML = `${toolbar("", "Tìm theo tòa nhà hoặc phòng học...")}
      <div class="notice" id="notice"></div>
      <div class="table-wrap"><table><thead><tr>
        <th data-sort="building">Tòa nhà ↕</th><th data-sort="room">Phòng học ↕</th>
        <th data-sort="normal">Số vi phạm phòng thường ↕</th><th data-sort="exam">Số vi phạm phòng thi ↕</th>
      </tr></thead><tbody id="tbody"></tbody></table></div>
      <div class="footer"><span id="summary"></span><div class="pagination" id="pagination"></div></div>`;
    bindCommon();
    document.getElementById("date-filter").addEventListener("change", applyFilter);
    document.getElementById("export-btn").addEventListener("click", exportCsv);
    applyFilter();
  }

  function renderUsers() {
    app.innerHTML = `${toolbar("", "Tìm tên, tài khoản, SĐT...")}
      <div class="notice" id="notice"></div>
      <div class="table-wrap"><table><thead><tr>
        <th>#</th><th>Họ tên</th><th>SĐT</th><th>Tài khoản</th><th>Vai trò</th><th>Trạng thái</th><th style="text-align:right">Tùy chọn</th>
      </tr></thead><tbody id="tbody"></tbody></table></div>
      <div class="footer"><span id="summary"></span><div class="pagination" id="pagination"></div></div>`;
    bindCommon();
    document.getElementById("export-btn").addEventListener("click", exportCsv);
    applyFilter();
  }

  function renderBuildings() {
    app.innerHTML = `${toolbar("", "Tìm tòa nhà...")}
      <div class="notice" id="notice"></div>
      <div class="table-wrap"><table><thead><tr>
        <th>#</th><th>Tòa nhà</th><th>Số phòng</th><th>Số camera</th><th>Trạng thái</th><th style="text-align:right">Tùy chọn</th>
      </tr></thead><tbody id="tbody"></tbody></table></div>
      <div class="footer"><span id="summary"></span><div class="pagination" id="pagination"></div></div>`;
    bindCommon();
    document.getElementById("export-btn").addEventListener("click", exportCsv);
    applyFilter();
  }

  function bindCommon() {
    document.getElementById("search").addEventListener("input", applyFilter);
    document.getElementById("sort-btn").addEventListener("click", () => {
      const keys = TYPE === "users" ? ["name","phone","username"] : TYPE === "buildings" ? ["name","rooms","cameras"] : ["building","room","normal","exam"];
      const idx = keys.indexOf(sortKey);
      sortKey = keys[(idx+1) % keys.length];
      sortDir = idx >= 0 && idx+1 < keys.length ? sortDir : 1;
      if (sortKey === keys[idx]) sortDir *= -1;
      applyFilter();
    });
    app.querySelectorAll("th[data-sort]").forEach(th => th.addEventListener("click", () => {
      const key = th.dataset.sort;
      sortDir = sortKey === key ? -sortDir : 1;
      sortKey = key;
      applyFilter();
    }));
  }

  function applyFilter() {
    const q = (document.getElementById("search")?.value || "").trim().toLowerCase();
    const date = document.getElementById("date-filter")?.value || "";
    filtered = rows.filter(r => {
      const hay = JSON.stringify(r).toLowerCase();
      const matchesText = !q || hay.includes(q);
      const matchesDate = TYPE !== "statistics" || !date || String(r.date || "") === date;
      return matchesText && matchesDate;
    });
    if (sortKey) filtered.sort((a,b) => {
      const av = a[sortKey], bv = b[sortKey];
      if (typeof av === "number" && typeof bv === "number") return (av-bv)*sortDir;
      return String(av??"").localeCompare(String(bv??""), "vi")*sortDir;
    });
    page = 1;
    drawRows();
  }

  function drawRows() {
    const start = (page-1)*pageSize;
    const view = filtered.slice(start,start+pageSize);
    const tbody = document.getElementById("tbody");
    if (!view.length) tbody.innerHTML = `<tr><td colspan="8"><div class="empty">Không có dữ liệu phù hợp.</div></td></tr>`;
    else if (TYPE === "users") tbody.innerHTML = view.map(userRow).join("");
    else if (TYPE === "buildings") tbody.innerHTML = view.map(buildingRow).join("");
    else tbody.innerHTML = view.map(statRow).join("");
    document.getElementById("summary").textContent = `Hiển thị ${filtered.length ? start+1 : 0}–${Math.min(start+view.length,filtered.length)} trên tổng ${filtered.length} bản ghi`;
    drawPagination();
    bindRows();
  }

  function statRow(r) {
    return `<tr><td>${esc(r.building)}</td><td>${esc(r.room)}</td><td><strong>${esc(r.normal)}</strong></td><td><strong>${esc(r.exam)}</strong></td></tr>`;
  }
  function buildingRow(r,i) {
    const status = Number(r.status) ? `<span class="badge active">Đang hoạt động</span>` : `<span class="badge inactive">Tạm dừng</span>`;
    return `<tr><td>${esc((page-1)*pageSize+i+1)}</td><td><strong>${esc(r.name)}</strong><span class="muted">ID #${esc(r.id)}</span></td><td>${esc(r.rooms)}</td><td>${esc(r.cameras)}</td><td>${status}</td><td><div class="actions"><button class="icon-btn" data-action="view-building" data-id="${r.id}" title="Xem chi tiết">${icon("visibility")}</button></div></td></tr>`;
  }
  function userRow(u,i) {
    const role = roleName(u.role);
    const avatar = u.avatar || "";
    const status = Number(u.status) ? `<span class="badge active">Hoạt động</span>` : `<span class="badge inactive">Đã khóa</span>`;
    return `<tr><td>${esc((page-1)*pageSize+i+1)}</td><td><div class="person">${avatar?`<img class="avatar" src="${esc(avatar)}">`:`<div class="avatar"></div>`}<div><strong>${esc(u.name)}</strong><span class="muted">ID #${esc(u.id)}</span></div></div></td><td>${esc(u.phone||"—")}</td><td><strong>${esc(u.username)}</strong></td><td><select class="select role-select" data-id="${u.id}"><option value="0" ${u.role===0?"selected":""}>Admin</option><option value="1" ${u.role===1?"selected":""}>Giảng viên</option><option value="2" ${u.role===2?"selected":""}>Bảo vệ</option></select></td><td>${status}</td><td><div class="actions"><button class="icon-btn" data-action="reset" data-id="${u.id}" title="Đặt lại mật khẩu">${icon("lock_reset")}</button><button class="icon-btn" data-action="lock" data-id="${u.id}" title="Khóa/Mở khóa">${icon(Number(u.status)?"lock":"lock_open")}</button><button class="icon-btn danger" data-action="delete" data-id="${u.id}" title="Xóa">${icon("delete")}</button></div></td></tr>`;
  }

  function bindRows() {
    app.querySelectorAll(".role-select").forEach(sel => sel.addEventListener("change", async e => {
      const id = Number(e.target.dataset.id), role = Number(e.target.value);
      await request(`/admin/users/${id}/role`, "PUT", {role});
    }));
    app.querySelectorAll("[data-action]").forEach(btn => btn.addEventListener("click", () => {
      const action = btn.dataset.action, id = Number(btn.dataset.id);
      if (action === "reset") openModal("Đặt lại mật khẩu", "Nhập mật khẩu mới cho tài khoản này.", "password", async value => {
        if (!value || value.length < 6) return showNotice("Mật khẩu mới cần ít nhất 6 ký tự.");
        await request(`/admin/users/${id}/password`, "PUT", {password:value});
      });
      if (action === "lock") openModal("Thay đổi trạng thái", "Bạn có muốn khóa/mở khóa tài khoản này?", "confirm", async () => {
        const u=rows.find(x=>x.id===id); await request(`/admin/users/${id}/status`, "PUT", {status:Number(u.status)?0:1});
      });
      if (action === "delete") openModal("Xóa tài khoản", "Thao tác này sẽ xóa tài khoản khỏi cơ sở dữ liệu.", "confirm", async () => await request(`/admin/users/${id}`, "DELETE"));
      if (action === "view-building") showNotice("Bảng này hiển thị số phòng và camera hiện có của từng tòa nhà.");
    }));
  }

  function drawPagination() {
    const pages = Math.max(1,Math.ceil(filtered.length/pageSize));
    page=Math.min(page,pages);
    const p=document.getElementById("pagination");
    let html=`<button class="page-btn" data-page="${Math.max(1,page-1)}">‹</button>`;
    for(let i=1;i<=pages;i++) if(i<=5 || i===pages) html += `<button class="page-btn ${i===page?"active":""}" data-page="${i}">${i}</button>`;
    html+=`<button class="page-btn" data-page="${Math.min(pages,page+1)}">›</button>`;
    p.innerHTML=html;
    p.querySelectorAll("[data-page]").forEach(b=>b.addEventListener("click",()=>{page=Number(b.dataset.page);drawRows()}));
  }

  async function request(path, method="GET", body=null) {
    try {
      const res=await fetch(API+path,{method,headers:{"Content-Type":"application/json"},body:body?JSON.stringify(body):undefined});
      const data=await res.json();
      if(!res.ok || data.success===false) throw new Error(data.message||"Thao tác thất bại");
      if(TYPE === "users") rows = await fetchRows("/admin/users");
      if(TYPE === "buildings") rows = await fetchRows("/admin/buildings");
      applyFilter();
      showNotice("Đã cập nhật dữ liệu.", false);
    } catch(err) { showNotice("Không thể kết nối API: "+err.message); }
  }
  async function fetchRows(path) {
    const res=await fetch(API+path); if(!res.ok) throw new Error("API không phản hồi"); return await res.json();
  }

  function showNotice(text,error=true) { const n=document.getElementById("notice"); if(!n)return; n.textContent=text; n.style.display="block"; n.style.background=error?"#fff7ed":"#edf9f1"; n.style.color=error?"#9a3412":"#166534"; setTimeout(()=>n.style.display="none",3000); }

  function openModal(title,text,type,callback) {
    pendingAction=callback; modalTitle.textContent=title; modalText.textContent=text; modalInput.style.display=type==="password"?"block":"none"; modalInput.value=""; modal.classList.add("show");
  }
  document.getElementById("modal-cancel").onclick=()=>{modal.classList.remove("show");pendingAction=null};
  document.getElementById("modal-ok").onclick=async()=>{const cb=pendingAction; modal.classList.remove("show");pendingAction=null; if(cb) await cb(modalInput.value)};

  function exportCsv() {
    const data=filtered; if(!data.length)return;
    const keys=TYPE==="users"?["id","name","phone","username","role","status"]:TYPE==="buildings"?["id","name","rooms","cameras","status"]:["building","room","normal","exam"];
    const lines=[keys.join(",")].concat(data.map(r=>keys.map(k=>`"${String(k==="role"?roleName(r[k]):r[k]??"").replaceAll('"','""')}"`).join(",")));
    const blob=new Blob(["\ufeff"+lines.join("\n")],{type:"text/csv;charset=utf-8"}); const a=document.createElement("a"); a.href=URL.createObjectURL(blob); a.download=`eduwatch_${TYPE}.csv`; a.click(); URL.revokeObjectURL(a.href);
  }

  render();
})();
