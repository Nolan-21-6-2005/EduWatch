(() => {
  const feed = document.getElementById("feed");
  const data = Array.isArray(window.__VIOLATIONS__) ? window.__VIOLATIONS__ : [];
  const API = window.__API__;

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
    const confidence = Number(row.confidence || 0) * 100;
    const thumb = row.image
      ? `<img src="${esc(row.image)}" alt="Ảnh bằng chứng">`
      : `<div class="violation-evidence-empty">Không có ảnh</div>`;
    // Một dòng vị trí: tòa nhà · phòng · camera.
    const place = [row.building, row.room, row.camera].filter(v => v && v !== "--").join(" · ");
    const footer = row.review_status === "pending"
      ? `<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded" rel="stylesheet">
          <div class="violation-actions">
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
            <span class="violation-confidence" title="Độ tin cậy">
              ${confidence.toFixed(0)}%
            </span>
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

  function render() {
    feed.innerHTML = data.length
      ? data.map(card).join("")
      : `<div class="violation-empty">Chưa có vi phạm trong cơ sở dữ liệu.</div>`;
    feed.querySelectorAll(".violation-actions button").forEach(btn => {
      btn.addEventListener("click", () => review(Number(btn.closest(".violation-card").dataset.id), btn.dataset.status, btn));
    });
  }

  async function review(id, status, button) {
    button.disabled = true;
    try {
      const response = await fetch(`${API}/violations/${id}/review`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({status})
      });
      if (!response.ok) throw new Error("Không thể cập nhật trạng thái.");
      window.location.reload();
    } catch (error) {
      button.disabled = false;
      alert(error.message);
    }
  }
  renderBanner();
  render();
})();