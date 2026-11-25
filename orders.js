(() => {
  const API = "https://saytim-uchun.onrender.com";
  const token = () => sessionStorage.getItem("blip_jwt");
  const headers = () => {
    const h = { "Content-Type": "application/json" };
    if (token()) h.Authorization = "Bearer " + token();
    return h;
  };
  const esc = (v) => String(v ?? "").replace(/[&<>"']/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
  }[c]));
  const statusText = {
    new: "Yangi", reviewing: "Ko‘rib chiqilmoqda", priced: "Narx belgilandi",
    in_progress: "Bajarilmoqda", completed: "Tayyor", cancelled: "Bekor qilindi"
  };
  const paymentText = { unpaid: "To‘lov kutilmoqda", awaiting: "To‘lov tekshirilmoqda", paid: "To‘langan", refunded: "Kredit qaytarilgan" };

  function init() {
    const tabs = document.querySelector(".tabs");
    const home = document.getElementById("t-home");
    const root = document.querySelector(".c");
    if (!tabs || !home || !root || document.getElementById("tab-orders")) return;

    const tab = document.createElement("div");
    tab.className = "tab";
    tab.id = "tab-orders";
    tab.textContent = "🧾 Buyurtma";
    tab.addEventListener("click", () => window.sw("orders", tab));
    tabs.appendChild(tab);

    const homeCard = document.createElement("div");
    homeCard.className = "gc";
    homeCard.innerHTML = '<span class="i">🧾</span><h3>Dastur buyurtma qilish</h3><p>Sayt, ilova yoki boshqa dastur uchun buyurtma yuboring.</p>';
    homeCard.addEventListener("click", () => window.sw("orders"));
    home.appendChild(homeCard);

    const section = document.createElement("div");
    section.className = "tc";
    section.id = "t-orders";
    section.innerHTML = `
      <style>
        .order-grid{display:grid;grid-template-columns:1fr;gap:12px}
        .order-field{width:100%;padding:12px;border:1px solid var(--brd);border-radius:10px;background:var(--bg);color:var(--text);font:inherit;margin:7px 0 12px}
        .order-card{background:var(--card);border:1px solid var(--brd);border-radius:14px;padding:14px;margin:10px 0}
        .order-meta{font-size:12px;color:var(--muted);margin:6px 0}
        .order-status{display:inline-block;border:1px solid var(--brd);border-radius:20px;padding:4px 9px;font-size:12px;margin:4px 4px 4px 0}
        .order-message{font-size:13px;color:var(--muted);margin:10px 0}
      </style>
      <div class="card">
        <div class="result-title">🧾 Yangi buyurtma</div>
        <p class="info">Buyurtmangizni yuboring. Biz talablarni ko‘rib chiqib, narxni TJS'da belgilaymiz. Hozircha yuborish bepul.</p>
        <form id="blipOrderForm">
          <label for="orderType">Xizmat turi</label>
          <select class="order-field" id="orderType" required>
            <option value="website">Veb-sayt</option>
            <option value="android_app">Android ilova</option>
            <option value="telegram_bot">Telegram bot</option>
            <option value="python_program">Python dastur</option>
            <option value="other">Boshqa loyiha</option>
          </select>
          <label for="orderTitle">Loyiha nomi</label>
          <input class="order-field" id="orderTitle" maxlength="100" minlength="2" placeholder="Masalan: Onlayn do‘kon sayti" required>
          <label for="orderDetails">Nima kerakligini batafsil yozing</label>
          <textarea class="order-field" id="orderDetails" rows="5" maxlength="3000" minlength="10" placeholder="Kerakli funksiyalar, dizayn va boshqa talablar..." required></textarea>
          <label for="orderContact">Bog‘lanish uchun (ixtiyoriy)</label>
          <input class="order-field" id="orderContact" maxlength="120" placeholder="Telegram username yoki email">
          <button class="btn" id="orderSubmit" type="submit">Buyurtmani yuborish</button>
          <p class="order-message" id="orderFormMessage" role="status"></p>
        </form>
      </div>
      <div class="card">
        <div class="result-title">📦 Mening buyurtmalarim</div>
        <button class="btn" id="refreshMyOrders" type="button">Yangilash</button>
        <div id="myOrdersList" class="order-message">Buyurtmalar yuklanmoqda...</div>
      </div>`;
    home.insertAdjacentElement("afterend", section);

    document.getElementById("blipOrderForm").addEventListener("submit", submitOrder);
    document.getElementById("refreshMyOrders").addEventListener("click", loadMyOrders);
    loadMyOrders();
  }

  async function submitOrder(event) {
    event.preventDefault();
    const button = document.getElementById("orderSubmit");
    const message = document.getElementById("orderFormMessage");
    button.disabled = true;
    button.textContent = "Yuborilmoqda...";
    message.textContent = "";
    const payload = {
      service_type: document.getElementById("orderType").value,
      title: document.getElementById("orderTitle").value.trim(),
      details: document.getElementById("orderDetails").value.trim(),
      contact: document.getElementById("orderContact").value.trim()
    };
    try {
      const res = await fetch(API + "/api/orders", {
        method: "POST", headers: headers(), credentials: "include", body: JSON.stringify(payload)
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Buyurtma yuborilmadi (" + res.status + ")");
      document.getElementById("blipOrderForm").reset();
      message.textContent = "Buyurtma qabul qilindi! ID: " + data.order_id;
      await loadMyOrders();
    } catch (err) {
      message.textContent = err.message;
    } finally {
      button.disabled = false;
      button.textContent = "Buyurtmani yuborish";
    }
  }

  async function loadMyOrders() {
    const box = document.getElementById("myOrdersList");
    if (!box) return;
    box.textContent = "Yuklanmoqda...";
    try {
      const res = await fetch(API + "/api/orders/mine", {
        headers: headers(), credentials: "include", cache: "no-store"
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Buyurtmalar olinmadi");
      if (!data.orders?.length) {
        box.textContent = "Hozircha buyurtmalaringiz yo‘q.";
        return;
      }
      box.innerHTML = data.orders.map(order => `
        <article class="order-card" data-order-id="${esc(order.id)}">
          <b>${esc(order.title)}</b>
          <div class="order-meta">ID: ${esc(order.id)}</div>
          <span class="order-status">${esc(statusText[order.status] || order.status)}</span>
          <span class="order-status">${esc(paymentText[order.payment_status] || order.payment_status)}</span>
          <div class="order-meta">Narx: ${order.price_tjs == null ? "Hali belgilanmagan" : esc(order.price_tjs) + " TJS"}</div>
          <p>${esc(order.details)}</p>
          ${order.delivery_url && order.payment_status === "paid" ? '<p><a target="_blank" rel="noopener" href="' + esc(order.delivery_url) + '">Tayyor fayllarni olish</a></p>' : ""}
        </article>`).join("");
    } catch (err) {
      box.textContent = err.message;
    }
  }

  document.addEventListener("DOMContentLoaded", init);
})();
