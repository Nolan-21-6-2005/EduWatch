(() => {
  const feed = document.getElementById("feed");
  const API = window.__API__ || "";
  const SESSION = window.__SESSION__ || "";
  let data = Array.isArray(window.__VIOLATIONS__) ? window.__VIOLATIONS__ : [];
  let version = Number(window.__VERSION__);
  if (!Number.isFinite(version)) version = -1;

  // Font icon nạp một lần (trước đây nằm lặp lại trong từng thẻ), cùng hiệu ứng thẻ mới / mất kết nối.
  const icons = document.createElement("link");
  icons.rel = "stylesheet";
  icons.href = "https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded";
  document.head.appendChild(icons);
  const extra = document.createElement("style");
  extra.textContent = `
    @keyframes ew-new { from { background: #e3f4e8; transform: translateY(-6px); opacity: .4; } to { background: transparent; transform: none; opacity: 1; } }
    .violation-card.ew-new { animation: ew-new .7s ease-out; }
    .violation-live-dot.offline { background: #c4524a !important; animation: none !important; }`;
  document.head.appendChild(extra);

  const esc = v => String(v ?? "").replace(/[&<>'"]/g, c =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;","\"":"&quot;"}[c])
  );
  // "2026-10-28 08:03:05" -> "28/10/2026 08:03:05" (giữ nguyên nếu không đúng định dạng)
  const fmtTime = v => {
    const m = String(v ?? "").match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}:\d{2}:\d{2})/);
    return m ? `${m[3]}/${m[2]}/${m[1]} ${m[4]}` : String(v ?? "--");
  };
  const reviewed = {confirmed: ["✓ Đã xác nhận", "confirmed"], wrong: ["× Đã báo sai AI", "wrong"]};

  function card(row) {
    const thumb = row.image
      ? `<img src="${esc(row.image)}" alt="Ảnh bằng chứng">`
      : `<div class="violation-evidence-empty">Không có ảnh</div>`;
    // Một dòng vị trí: tòa nhà · phòng · camera.
    const place = [row.building, row.room, row.camera].filter(v => v && v !== "--").join(" · ");
    const footer = row.review_status === "pending"
      ? `<div class="violation-actions">
            <button class="confirm" data-status="confirmed" title="Xác nhận">
              <span class="material-symbols-rounded">check</span>
            </button>
            <button class="wrong" data-status="wrong" title="Báo sai">
              <span class="material-symbols-rounded">close</span>
            </button>
          </div>`
      : (r => r ? `<div class="violation-reviewed ${r[1]}">${r[0]}</div>` : "")(reviewed[row.review_status]);

    return `<article class="violation-card" data-id="${row.id}">
      <div class="violation-card-body">
        <div class="violation-thumb">${thumb}</div>
        <div class="violation-info">
          <div class="violation-head">
            <div class="violation-name" title="${esc(row.title)}">
              ${esc(row.title)}
            </div>
          </div>
          <div class="violation-place" title="${esc(place)}">
            ${esc(place)}
          </div>
          <div class="violation-time">
            ${esc(fmtTime(row.datetime_display))}
          </div>
        </div>
        ${footer}
      </div>
    </article>`;
  }

  function renderBanner() {
    const banner = document.getElementById("banner");
    const pending = Number(window.__PENDING__ || 0);
    if (!banner) return;
    banner.classList.toggle("clear", pending === 0);
    banner.textContent = pending > 0
      ? `Có ${pending} vi phạm chưa xử lý.`
      : "Không có vi phạm nào đang chờ xử lý.";
  }

  function toElement(html) {
    const tpl = document.createElement("template");
    tpl.innerHTML = html.trim();
    return tpl.content.firstElementChild;
  }

  // Chỉ thêm/sửa/xóa đúng thẻ thay đổi để ảnh không nhấp nháy khi có log mới.
  function sync(rows, animate) {
    const empty = feed.querySelector(".violation-empty");
    if (!rows.length) {
      feed.innerHTML = `<div class="violation-empty">Chưa có vi phạm trong cơ sở dữ liệu.</div>`;
      return;
    }
    if (empty) empty.remove();
    const wanted = new Set(rows.map(r => String(r.id)));
    [...feed.children].forEach(el => { if (!wanted.has(el.dataset.id)) el.remove(); });
    rows.forEach((row, index) => {
      const html = card(row);
      let el = feed.querySelector(`[data-id="${row.id}"]`);
      if (!el) {
        el = toElement(html);
        el.dataset.sig = html;
        if (animate) el.classList.add("ew-new");
      } else if (el.dataset.sig !== html) {
        const next = toElement(html);
        next.dataset.sig = html;
        el.replaceWith(next);
        el = next;
      }
      if (feed.children[index] !== el) feed.insertBefore(el, feed.children[index] || null);
    });
  }

  feed.addEventListener("click", event => {
    const btn = event.target.closest(".violation-actions button");
    if (!btn) return;
    review(Number(btn.closest(".violation-card").dataset.id), btn.dataset.status, btn);
  });

  async function review(id, status, button) {
    button.disabled = true;
    try {
      const response = await fetch(`${API}/violations/${id}/review`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({status})
      });
      if (!response.ok) throw new Error("Không thể cập nhật trạng thái.");
      refresh(true);
    } catch (error) {
      button.disabled = false;
      alert(error.message);
    }
  }

  const dot = document.querySelector(".violation-live-dot");
  const setLive = ok => { if (dot) dot.classList.toggle("offline", !ok); };

  let busy = false;
  async function refresh(force) {
    if (busy) return;
    busy = true;
    try {
      const qs = new URLSearchParams({limit: "8"});
      if (SESSION) qs.set("session", SESSION);
      if (!force && version >= 0) qs.set("since", String(version));  // chưa đổi: backend trả ngay
      const response = await fetch(`${API}/violations/live?${qs}`, {cache: "no-store"});
      if (!response.ok) throw new Error("live");
      const result = await response.json();
      setLive(true);
      if (result.changed === false) return;
      const firstLoad = version < 0;
      version = result.version;
      window.__PENDING__ = result.pending;
      renderBanner();
      sync(result.rows, !firstLoad);
    } catch (error) {
      setLive(false);  // backend tạm thời không phản hồi: thử lại ở lần sau
    } finally {
      busy = false;
    }
  }

  renderBanner();
  sync(data, false);
  // Hỏi phiên bản mỗi giây (request rất nhẹ); mỗi 10 giây tải lại đầy đủ để bắt thay đổi
  // ghi trực tiếp vào DB bởi tiến trình khác. Tạm dừng khi tab/iframe bị ẩn.
  let tick = 0;
  setInterval(() => {
    if (document.hidden) return;
    tick += 1;
    refresh(tick % 10 === 0);
  }, 1000);
  document.addEventListener("visibilitychange", () => { if (!document.hidden) refresh(true); });
  refresh(true);
})();
