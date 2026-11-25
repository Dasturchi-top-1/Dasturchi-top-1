(() => {
  const API = "https://saytim-uchun.onrender.com";
  const token = () => sessionStorage.getItem("blip_jwt");
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[c]));
  const statuses = [
    ["new","Yangi"],["reviewing","Ko‘rib chiqilmoqda"],["priced","Narx belgilandi"],
    ["in_progress","Bajarilmoqda"],["completed","Tayyor"],["cancelled","Bekor qilindi"]
  ];
  const payments = [["unpaid","To‘lanmagan"],["awaiting","Tekshirilmoqda"],["paid","To‘langan"]];
  const serviceNames = {website:"Veb-sayt",android_app:"Android ilova",telegram_bot:"Telegram bot",python_program:"Python dastur",other:"Boshqa loyiha"};

  function init() {
    const monitor = document.querySelector(".monitor-card");
    if (!monitor || document.getElementById("adminOrdersCard")) return;
    const card = document.createElement("section");
    card.className = "monitor-card";
    card.id = "adminOrdersCard";
    card.innerHTML = `
      <div class="monitor-title">🧾 BLIP BUYURTMALAR <span id="newOrderCount" class="monitor-muted"></span></div>
      <p class="monitor-muted" style="margin-bottom:12px">Narxni TJS'da kiriting. To‘lovni faqat haqiqiy tushumni tekshirgandan keyin “To‘langan” deb belgilang.</p>
      <div id="adminOrdersList" class="monitor-muted">Buyurtmalar yuklanmoqda...</div>
      <button class="btn" id="refreshAdminOrders" type="button">Buyurtmalarni yangilash</button>`;
    monitor.insertAdjacentElement("afterend", card);
    document.getElementById("refreshAdminOrders").addEventListener("click", loadOrders);
    loadOrders();
    setInterval(loadOrders, 30000);
  }

  async function loadOrders() {
    const box = document.getElementById("adminOrdersList");
    if (!box) return;
    try {
      const res = await fetch(API + "/api/admin/orders", {
        headers: { Authorization: "Bearer " + token() }, cache: "no-store"
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Server xatosi: " + res.status);
      const orders = data.orders || [];
      const fresh = orders.filter(o => o.status === "new").length;
      document.getElementById("newOrderCount").textContent = fresh ? "· " + fresh + " ta yangi" : "";
      if (!orders.length) {
        box.textContent = "Hozircha buyurtmalar yo‘q.";
        return;
      }
      box.innerHTML = orders.map(o => `
        <article class="order-card" data-payment-method="${esc(o.payment_method || "manual")}" style="background:rgba(0,0,0,.18);border:1px solid var(--brd);border-radius:12px;padding:12px;margin:12px 0">
          <b>${esc(o.title)}</b>
          <div class="monitor-muted">ID: ${esc(o.id)} · ${esc(o.username || "Foydalanuvchi")} · ${esc(o.created_at)}</div>
          <div style="margin:8px 0"><b>Xizmat:</b> ${esc(serviceNames[o.service_type] || o.service_type)} · <b>Aloqa:</b> ${esc(o.contact || "Ko‘rsatilmagan")}</div>
          <p style="white-space:pre-wrap;margin:8px 0">${esc(o.details)}</p>
          <label>Holati</label>
          <select id="os-${esc(o.id)}" class="order-field">${statuses.map(([v,l]) => '<option value="' + v + '"' + (o.status===v?' selected':'') + '>' + l + '</option>').join("")}</select>
          <label>Narx (TJS)</label>
          <input id="op-${esc(o.id)}" class="order-field" type="number" min="0.01" step="0.01" value="${o.price_tjs == null ? "" : esc(o.price_tjs)}" placeholder="Masalan: 250">
          <label>To‘lov holati</label>
          <select id="pay-${esc(o.id)}" class="order-field">${payments.map(([v,l]) => '<option value="' + v + '"' + (o.payment_status===v?' selected':'') + '>' + l + '</option>').join("")}</select>
          <label>Admin izohi (ixtiyoriy)</label>
          <input id="note-${esc(o.id)}" class="order-field" maxlength="1000" value="${esc(o.admin_note || "")}" placeholder="Mijozga ko‘rinadigan izoh">
          <label>Tayyor fayl havolasi (faqat to‘lovdan keyin mijozga ko‘rinadi)</label>
          <input id="file-${esc(o.id)}" class="order-field" maxlength="1000" value="${esc(o.delivery_url || "")}" placeholder="Tayyor fayl havolasi">
          <button class="btn" type="button" data-save-order="${esc(o.id)}">Saqlash</button>
          ${o.status === "cancelled" && o.payment_status === "paid" && o.payment_method === "credits" ? '<button class="btn" type="button" data-refund-order="' + esc(o.id) + '">Kreditni qaytarish</button>' : ""}
          <p class="monitor-muted" id="msg-${esc(o.id)}"></p>
        </article>`).join("");
      box.querySelectorAll("[data-save-order]").forEach(btn => {
        btn.addEventListener("click", () => saveOrder(btn.getAttribute("data-save-order")));
      });
      box.querySelectorAll("[data-refund-order]").forEach(btn => {
        btn.addEventListener("click", () => refundOrder(btn.getAttribute("data-refund-order"), btn));
      });
    } catch (err) {
      box.textContent = err.message;
    }
  }

  async function refundOrder(id, button) {
    if (!window.confirm("Bekor qilingan buyurtma uchun sarflangan kreditlar foydalanuvchiga qaytarilsinmi?")) return;
    button.disabled = true;
    try {
      const res = await fetch(API + "/api/admin/orders/refund-credits", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: "Bearer " + token() },
        body: JSON.stringify({ order_id: id })
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Kredit qaytarilmadi");
      await loadOrders();
    } catch (err) {
      window.alert(err.message);
      button.disabled = false;
    }
  }

  async function saveOrder(id) {
    const msg = document.getElementById("msg-" + id);
    msg.textContent = "Saqlanmoqda...";
    const priceRaw = document.getElementById("op-" + id).value.trim();
    const payload = {
      id,
      status: document.getElementById("os-" + id).value,
      payment_status: document.getElementById("pay-" + id).value,
      admin_note: document.getElementById("note-" + id).value.trim(),
      delivery_url: document.getElementById("file-" + id).value.trim()
    };
    if (priceRaw !== "") payload.price_tjs = Number(priceRaw);
    try {
      const res = await fetch(API + "/api/admin/orders/update", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: "Bearer " + token() },
        body: JSON.stringify(payload)
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Saqlanmadi");
      msg.textContent = "Saqlandi.";
      await loadOrders();
    } catch (err) {
      msg.textContent = err.message;
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
