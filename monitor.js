/* BLIP Monitor — transparent, consent-based site analytics. */
(function () {
  "use strict";
  if (window.__blipMonitorLoaded) return;
  window.__blipMonitorLoaded = true;

  var API = "https://saytim-uchun.onrender.com";
  var CONSENT_KEY = "blip_monitor_consent";
  var page = (location.pathname.split("/").pop() || "index.html").split("?")[0];
  var timer = null;

  var style = document.createElement("style");
  style.textContent = [
    "#blip-monitor-ui{position:fixed;z-index:99990;right:14px;bottom:14px;font:13px/1.45 system-ui,sans-serif;color:#eef2ff}",
    "#blip-monitor-ui *{box-sizing:border-box}",
    "#blip-monitor-toggle{border:1px solid #475569;background:#111827;color:#e2e8f0;border-radius:999px;padding:9px 13px;box-shadow:0 8px 30px #0008;cursor:pointer}",
    "#blip-monitor-panel{display:none;width:min(340px,calc(100vw - 28px));margin-bottom:9px;padding:15px;border:1px solid #475569;border-radius:14px;background:#0b1020;box-shadow:0 12px 40px #000a}",
    "#blip-monitor-panel.open{display:block}",
    "#blip-monitor-panel strong{display:block;font-size:14px;margin-bottom:7px;color:#fff}",
    "#blip-monitor-panel p{margin:0 0 12px;color:#cbd5e1;font-size:12px}",
    ".blip-monitor-actions{display:flex;gap:8px;flex-wrap:wrap}",
    ".blip-monitor-actions button{border:0;border-radius:8px;padding:8px 11px;font-weight:700;cursor:pointer}",
    "#blip-monitor-accept{background:#34d399;color:#052e24}",
    "#blip-monitor-decline{background:#334155;color:#fff}",
    "#blip-monitor-settings{background:#1e293b;color:#e2e8f0}",
    "@media(max-width:600px){#blip-monitor-ui{right:8px;bottom:8px}#blip-monitor-toggle{font-size:11px;padding:8px 10px}}"
  ].join("");
  document.head.appendChild(style);

  var root = document.createElement("div");
  root.id = "blip-monitor-ui";
  root.innerHTML =
    '<div id="blip-monitor-panel" role="dialog" aria-label="BLIP sayt statistikasi">' +
      '<strong>Sayt faolligi statistikasi</strong>' +
      '<p>Rozilik bersangiz, sahifa nomi, ichki bo‘limga o‘tish va Black AI ochilgani qayd etiladi. Bu saytni yaxshilash uchun ishlatiladi. Xabar matni, parol, tugma ichidagi yozuvlar, GPS, kamera va mikrofon yozilmaydi. Admin faqat shu statistikani ko‘radi.</p>' +
      '<div class="blip-monitor-actions">' +
        '<button id="blip-monitor-accept" type="button">Roziman</button>' +
        '<button id="blip-monitor-decline" type="button">Rad etaman</button>' +
      '</div>' +
    '</div>' +
    '<button id="blip-monitor-toggle" type="button" aria-expanded="false">Maxfiylik sozlamalari</button>';
  document.body.appendChild(root);

  var panel = root.querySelector("#blip-monitor-panel");
  var toggle = root.querySelector("#blip-monitor-toggle");
  var accept = root.querySelector("#blip-monitor-accept");
  var decline = root.querySelector("#blip-monitor-decline");

  function openPanel(open) {
    panel.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", String(open));
    toggle.textContent = open ? "Yopish" : "Maxfiylik sozlamalari";
  }

  function authHeaders() {
    var headers = { "Content-Type": "application/json" };
    try {
      var token = sessionStorage.getItem("blip_jwt");
      if (token) headers.Authorization = "Bearer " + token;
    } catch (_) {}
    return headers;
  }

  function send(path, body) {
    return fetch(API + path, {
      method: "POST",
      headers: authHeaders(),
      credentials: "include",
      keepalive: true,
      body: JSON.stringify(Object.assign({ consent: true, page: page }, body || {}))
    }).catch(function () {});
  }

  function ping() {
    if (localStorage.getItem(CONSENT_KEY) !== "yes" || document.visibilityState === "hidden") return;
    send("/api/monitor/ping");
  }

  function event(name) {
    if (localStorage.getItem(CONSENT_KEY) !== "yes") return;
    send("/api/monitor/event", { event: name });
  }

  function start() {
    if (timer) clearInterval(timer);
    event("page_view");
    ping();
    timer = setInterval(ping, 45000);
  }

  function setChoice(choice) {
    try { localStorage.setItem(CONSENT_KEY, choice); } catch (_) {}
    openPanel(false);
    toggle.textContent = choice === "yes" ? "Statistika yoqilgan · sozlamalar" : "Statistika o‘chirilgan · sozlamalar";
    if (timer) clearInterval(timer);
    timer = null;
    if (choice === "yes") start();
  }

  toggle.addEventListener("click", function () {
    openPanel(!panel.classList.contains("open"));
  });
  accept.addEventListener("click", function () { setChoice("yes"); });
  decline.addEventListener("click", function () { setChoice("no"); });

  document.addEventListener("click", function (e) {
    var launch = e.target.closest && e.target.closest("#baiLaunch");
    if (launch) event("black_ai_open");

    var marked = e.target.closest && e.target.closest("[data-monitor-event='feature_open']");
    if (marked) event("feature_open");

    var link = e.target.closest && e.target.closest("a[href]");
    if (link) {
      try {
        var target = new URL(link.href, location.href);
        if (target.origin === location.origin && target.pathname.endsWith(".html") && target.pathname !== location.pathname) {
          event("internal_navigation");
        }
      } catch (_) {}
    }
  }, true);

  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") ping();
  });

  var choice = "unknown";
  try { choice = localStorage.getItem(CONSENT_KEY) || "unknown"; } catch (_) {}
  if (choice === "yes") {
    toggle.textContent = "Statistika yoqilgan · sozlamalar";
    start();
  } else if (choice === "no") {
    toggle.textContent = "Statistika o‘chirilgan · sozlamalar";
  } else {
    openPanel(true);
  }
})();