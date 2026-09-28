(() => {
  const feed = document.getElementById("feed");
  const data = Array.isArray(window.__VIOLATIONS__) ? window.__VIOLATIONS__ : [];
  const API = window.__API__;

  const esc = v => String(v ?? "").replace(/[&<>'"]/g, c =>
    ({"&":"&amp;","<":"&lt;",">":"&gt;","'":"&#39;","\"":"&quot;"}[c])
  );
  const status = s => ({
    pending: ["Chờ xác nhận", "pending"],
    confirmed: ["Đã xác nhận", "confirmed"],
    wrong: ["Báo sai AI", "wrong"]
  }[s] || ["Chờ xác nhận", "pending"]);

  function card(row) {
    const [statusText, statusClass] = status(row.review_status);
    const confidence = Number(row.confidence || 0) * 100;
    const evidence = row.image
      ? `<img src="${esc(row.image)}" alt="Ảnh bằng chứng">`
      : `<div class="violation-evidence-empty">Không có ảnh bằng chứng</div>`;

    return `<article class="violation-card" data-id="${row.id}">
      <div class="violation-card-top">
        <div class="violation-meta">
          <div class="violation-camera">${esc(row.camera)}</div>
          <div class="violation-time">${esc(row.datetime_display)}</div>
        </div>
        <span class="violation-status ${statusClass}">${statusText}</span>
      </div>
      <div class="violation-name">${esc(row.title)}</div>
      <div class="violation-location">${esc(row.building)} · ${esc(row.room)}</div>
      <div class="violation-evidence">
        ${evidence}
        <span class="violation-confidence">Độ tin cậy: ${confidence.toFixed(1)}%</span>
      </div>
      ${row.review_status === "pending" ? `
      <div class="violation-actions">
        <button class="confirm" data-status="confirmed">✓ Xác nhận</button>
        <button data-status="wrong">× Báo sai AI</button>
      </div>` : ""}
    </article>`;
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
  render();
})();