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

  function init() {
    const section = document.getElementById("t-orders");
    const firstCard = section?.querySelector(".card");
    if (!section || !firstCard || document.getElementById("blipCreditsCard")) return;
    const card = document.createElement("div");
    card.className = "card";
    card.id = "blipCreditsCard";
    card.innerHTML = `
      <div class="result-title">💠 BLIP Credits</div>
      <p class="info">1 TJS = 10 kredit. BLIP Credits — faqat Multiverse ichida loyiha xarid qilish uchun ishlatiladigan ichki kredit.</p>
      <div id="creditBalance" class="order-message">Balans yuklanmoqda...</div>
      <form id="creditPurchaseForm">
        <label for="creditAmountTjs">Kredit xaridi so‘rovi (TJS)</label>
        <input class="order-field" id="creditAmountTjs" type="number" min="0.10" max="10000" step="0.10" placeholder="Masalan: 10.00" required>
        <button class="btn" id="creditPurchaseSubmit" type="submit">Kredit so‘rovini yuborish</button>
        <p class="order-message">So‘rov yuborilgach, admin haqiqiy to‘lovni ota-ona/vasiy nazoratida tekshiradi. Tasdiqlanmaguncha kredit berilmaydi. Karta yoki bank maxfiy ma’lumotlarini bu yerga yozmang.</p>
      </form>
      <div id="creditPurchaseHistory" class="order-message"></div>
      <div id="creditTransactionHistory" class="order-message"></div>`;
    firstCard.before(card);
    document.getElementById("creditPurchaseForm").addEventListener("submit", submitPurchase);
    document.addEventListener("click", event => {
      const button = event.target.closest("[data-pay-order]");
      if (button) payOrder(button.getAttribute("data-pay-order"), button);
    });
    const list = document.getElementById("myOrdersList");
    if (list && window.MutationObserver) {
      new MutationObserver(addCheckoutButtons).observe(list, { childList: true, subtree: true });
      addCheckoutButtons();
    }
    loadWallet();
  }
  async function loadWallet() {
    const balance = document.getElementById("creditBalance");
    if (!balance) return;
    try {
      const res = await fetch(API + "/api/credits/wallet", {
        headers: headers(), credentials: "include", cache: "no-store"
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Kredit hamyoni olinmadi");
      balance.innerHTML = "<b>Balans: " + esc(data.wallet?.balance ?? 0) + " BLIP Credits</b>";
      document.getElementById("creditPurchaseHistory").innerHTML =
        "<b>Kredit so‘rovlari</b>" + ((data.purchases || []).length
          ? data.purchases.map(p => "<div class='order-meta'>" + esc(p.amount_tjs) + " TJS · " + esc(p.credits) + " kredit · " + esc(p.status) + "</div>").join("")
          : "<div class='order-meta'>Hozircha so‘rovlar yo‘q.</div>");
      document.getElementById("creditTransactionHistory").innerHTML =
        "<b>Oxirgi operatsiyalar</b>" + ((data.transactions || []).length
          ? data.transactions.map(t => "<div class='order-meta'>" + (Number(t.delta) > 0 ? "+" : "") + esc(t.delta) + " kredit · " + esc(t.note || t.kind) + "</div>").join("")
          : "<div class='order-meta'>Hozircha operatsiyalar yo‘q.</div>");
    } catch (err) {
      balance.textContent = err.message;
    }
  }
  async function submitPurchase(event) {
    event.preventDefault();
    const button = document.getElementById("creditPurchaseSubmit");
    const amountInput = document.getElementById("creditAmountTjs");
    const balance = document.getElementById("creditBalance");
    button.disabled = true;
    try {
      const amount = Number(amountInput.value);
      if (!Number.isFinite(amount) || amount < 0.10 || amount > 10000 ||
          Math.round(amount * 10) !== amount * 10) {
        throw new Error("Summa 0.10 TJS qadamida, 0.10–10 000 TJS oralig‘ida bo‘lishi kerak.");
      }
      const res = await fetch(API + "/api/credits/purchases", {
        method: "POST", headers: headers(), credentials: "include",
        body: JSON.stringify({ amount_tjs: amount.toFixed(2), idempotency_key: crypto.randomUUID() })
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Kredit so‘rovi yuborilmadi");
      amountInput.value = "";
      balance.textContent = "So‘rov yuborildi. To‘lov tasdiqlangach kredit qo‘shiladi.";
      await loadWallet();
    } catch (err) {
      balance.textContent = err.message;
    } finally {
      button.disabled = false;
    }
  }
  function addCheckoutButtons() {
    document.querySelectorAll("#myOrdersList .order-card").forEach(card => {
      if (card.querySelector("[data-pay-order]")) return;
      const states = card.querySelectorAll(".order-status");
      const metas = card.querySelectorAll(".order-meta");
      const id = card.getAttribute("data-order-id");
      const priceLine = Array.from(metas).find(el => el.textContent.trim().startsWith("Narx:"));
      if (!id || !states[0] || !states[1] || !priceLine) return;
      if (states[0].textContent.trim() !== "Narx belgilandi" ||
          states[1].textContent.trim() !== "To‘lov kutilmoqda") return;
      const price = Number(priceLine.textContent.replace("Narx:", "").replace("TJS", "").trim());
      if (!Number.isFinite(price) || price <= 0) return;
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn";
      btn.setAttribute("data-pay-order", id);
      btn.textContent = "To‘lash · " + Math.ceil(price * 10) + " kredit";
      card.appendChild(btn);
    });
  }
  async function payOrder(orderId, button) {
    if (!window.confirm("Ushbu buyurtma uchun BLIP Credits sarflansinmi?")) return;
    button.disabled = true;
    try {
      const res = await fetch(API + "/api/orders/pay-with-credits", {
        method: "POST", headers: headers(), credentials: "include",
        body: JSON.stringify({ order_id: orderId })
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.error || "Kredit bilan to‘lov bajarilmadi");
      await loadWallet();
      document.getElementById("refreshMyOrders")?.click();
    } catch (err) {
      window.alert(err.message);
      button.disabled = false;
    }
  }
  document.addEventListener("DOMContentLoaded", init);
})();