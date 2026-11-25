(() => {
  const API = "https://saytim-uchun.onrender.com";
  const token = () => sessionStorage.getItem("blip_jwt");
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[c]));
  function init() {
    const ordersCard = document.getElementById("adminOrdersCard");
    if (!ordersCard || document.getElementById("adminCreditPurchasesCard")) return;
    const card = document.createElement("section");
    card.className = "monitor-card";
    card.id = "adminCreditPurchasesCard";
    card.innerHTML = `
      <div class="monitor-title">💠 BLIP CREDITS · XARID SO‘ROVLARI</div>
      <p class="monitor-muted">Haqiqiy to‘lovni ota-ona/vasiy bilan tekshirmasdan so‘rovni tasdiqlamang. Sayt karta yoki bank maxfiy ma’lumotlarini yig‘maydi.</p>
      <div id="adminCreditPurchasesList" class="monitor-muted">So‘rovlar yuklanmoqda...</div>
      <button class="btn" id="refreshCreditPurchases" type="button">Kredit so‘rovlarini yangilash</button>`;
    ordersCard.insertAdjacentElement("afterend", card);
    document.getElementById("refreshCreditPurchases").addEventListener("click", loadPurchases);
    card.addEventListener("click", event => {
      const button = event.target.closest("[data-credit-review]");
      if (button) reviewPurchase(button.getAttribute("data-id"), button.getAttribute("data-credit-review"), button);
    });
    loadPurchases();
    setInterval(loadPurchases, 30000);
  }
  async function loadPurchases() {
    const box = document.getElementById("adminCreditPurchasesList");
    if (!box) return;
    try {
      const res = await fetch(API + "/api/admin/credits/purchases", {
        headers: { Authorization: "Bearer " + token() }, cache: "no-store"
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Kredit so‘rovlari olinmadi");
      const pending = (data.purchases || []).filter(p => p.status === "pending");
      if (!pending.length) {
        box.textContent = "Kutilayotgan kredit so‘rovlari yo‘q.";
        return;
      }
      box.innerHTML = pending.map(p => `
        <article class="order-card" style="border:1px solid var(--brd);border-radius:12px;padding:12px;margin:10px 0">
          <b>${esc(p.username || "Foydalanuvchi")}</b>
          <div class="monitor-muted">${esc(p.amount_tjs)} TJS → ${esc(p.credits)} BLIP Credits</div>
          <div class="monitor-muted">${esc(p.created_at)}</div>
          <button class="btn" type="button" data-id="${esc(p.id)}" data-credit-review="approved">To‘lov tekshirildi · Tasdiqlash</button>
          <button class="btn" type="button" data-id="${esc(p.id)}" data-credit-review="rejected">Rad etish</button>
        </article>`).join("");
    } catch (err) {
      box.textContent = err.message;
    }
  }
  async function reviewPurchase(id, decision, button) {
    const message = decision === "approved"
      ? "To‘lovni haqiqatan tekshirdingizmi? Tasdiqlangach kredit foydalanuvchiga qo‘shiladi."
      : "Kredit xaridi so‘rovi rad etilsinmi?";
    if (!window.confirm(message)) return;
    button.disabled = true;
    try {
      const res = await fetch(API + "/api/admin/credits/purchases/review", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: "Bearer " + token() },
        body: JSON.stringify({ id, decision })
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "So‘rov yangilanmadi");
      await loadPurchases();
    } catch (err) {
      window.alert(err.message);
      button.disabled = false;
    }
  }
  document.addEventListener("DOMContentLoaded", init);
})();